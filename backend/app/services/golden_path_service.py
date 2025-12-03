import networkx as nx
import json
import time

class GoldenPathService:
    def __init__(self):
        self.graph = None
        self.last_build_time = None
        self.cache_duration = 300 # 5 minutes

    def get_graph(self):
        """Returns cached graph or rebuilds if expired."""
        now = time.time()
        if self.graph is None or (self.last_build_time and now - self.last_build_time > self.cache_duration):
            self.graph = self.build_graph()
            self.last_build_time = now
        return self.graph

    def build_graph(self, user_id=1):
        """
        Constructs the Syllabus Graph dynamically.
        Optimized to use bulk aggregation and integrate Weak Areas.
        """
        G = nx.DiGraph()
        
        try:
            from app.db import get_db
            conn = get_db()
            
            # 1. Bulk Fetch Data (Avoid N+1 Queries)
            topics_data = conn.execute('SELECT id, topic, subject, status FROM syllabus_topics').fetchall()
            if not topics_data: return G
            
            # Aggregate PYQ Counts
            pyq_counts = {}
            rows = conn.execute('SELECT topic, COUNT(*) as c FROM pyq_questions GROUP BY topic').fetchall()
            for r in rows: pyq_counts[r['topic']] = r['c']
            
            # Aggregate Flashcard Counts (Approximate matching for tags)
            fc_rows = conn.execute('SELECT tags FROM flashcards').fetchall()
            fc_counts = {}
            for r in fc_rows:
                if r['tags']:
                    for tag in r['tags'].split(','):
                        t = tag.strip()
                        fc_counts[t] = fc_counts.get(t, 0) + 1
            
            # Fetch Weak Areas
            weak_areas = {}
            wa_rows = conn.execute('SELECT topic, priority_score FROM weak_area_analysis WHERE user_id = ?', (user_id,)).fetchall()
            for r in wa_rows: weak_areas[r['topic']] = r['priority_score']

            # 2. Build Nodes with Dynamic Weights
            for row in topics_data:
                topic_name = row['topic']
                subject = row['subject'] or "General"
                
                # Metrics
                raw_yield = pyq_counts.get(topic_name, 0)
                raw_effort = fc_counts.get(topic_name, 0)
                weakness_score = weak_areas.get(topic_name, 0) # 0-100
                
                # Normalization
                yield_score = min(raw_yield * 5, 100)
                effort_score = min(max(raw_effort * 2, 10), 100)
                
                # Dynamic Adjustment: Weak areas boost "Effective Yield" (High priority to fix)
                weakness_multiplier = 1.0 + (weakness_score / 50.0) 
                effective_yield = yield_score * weakness_multiplier
                
                # ROI Calculation
                roi = effective_yield / effort_score if effort_score > 0 else 0
                
                G.add_node(
                    row['id'], 
                    label=topic_name, 
                    yield_val=yield_score,
                    effective_yield=effective_yield,
                    effort=effort_score,
                    weakness=weakness_score,
                    roi=roi,
                    group=subject,
                    status=row['status']
                )
                
            # 3. Define Dependencies (Edges)
            # Link topics within the same subject sequentially
            subjects = {}
            for row in topics_data:
                sub = row['subject'] or "General"
                if sub not in subjects: subjects[sub] = []
                subjects[sub].append(row['id'])
                
            for sub, topic_ids in subjects.items():
                for i in range(len(topic_ids) - 1):
                    G.add_edge(topic_ids[i], topic_ids[i+1])

        except Exception as e:
            print(f"Golden Path Build Error: {e}")
            import traceback
            traceback.print_exc()
            
        return G

    def apply_bio_weights(self, bio_status):
        """
        Adjusts graph weights based on user's current Bio-Status.
        Low Energy -> High Cost for High Effort nodes.
        High Energy -> Bonus for High Yield nodes.
        """
        G = self.get_graph()
        if not G: return

        energy = bio_status.get('energy_level', 50)
        
        for node in G.nodes:
            data = G.nodes[node]
            base_cost = data.get('effort', 10)
            
            # Dynamic Cost Calculation
            if energy < 30:
                # Low Energy: High effort tasks are very expensive
                adjusted_cost = base_cost * 2.0 if base_cost > 50 else base_cost
            elif energy > 80:
                # High Energy: High effort tasks are cheaper (flow state)
                adjusted_cost = base_cost * 0.7
            else:
                adjusted_cost = base_cost
                
            eff_yield = data.get('effective_yield', 1)
            if eff_yield == 0: eff_yield = 0.1
            
            # Cost Function for Pathfinding (Minimizing Cost = Maximizing ROI)
            # Cost = Effort / Yield
            weight = adjusted_cost / eff_yield
            
            G.nodes[node]['weight'] = weight

    def get_optimal_path(self, start_node_id=None, end_node_id=None):
        """
        Finds the 'Golden Path' using Dijkstra's algorithm on dynamic weights.
        """
        G = self.get_graph()
        if not G: return []
        
        # If no start/end, try to find from 'General' to leaf
        if not start_node_id:
            roots = [n for n, d in G.in_degree() if d == 0]
            if roots: start_node_id = roots[0]
            
        if not end_node_id:
            leaves = [n for n, d in G.out_degree() if d == 0]
            if leaves: end_node_id = leaves[0]
            
        if not start_node_id or not end_node_id:
            return []
            
        try:
            # Ensure weights exist (default to 1 if not set by bio_weights)
            for u, v, d in G.edges(data=True):
                if 'weight' not in G.nodes[u]:
                    G.nodes[u]['weight'] = 1.0
            
            path = nx.shortest_path(G, source=start_node_id, target=end_node_id, weight='weight')
            
            # Enrich path with node data
            full_path = []
            for node_id in path:
                node_data = G.nodes[node_id]
                full_path.append({
                    "id": node_id,
                    "label": node_data['label'],
                    "action": "STUDY",
                    "reason": f"High ROI ({round(node_data.get('roi',0), 1)}) path segment."
                })
            return full_path
        except nx.NetworkXNoPath:
            return []
        except Exception as e:
            print(f"Pathfinding Error: {e}")
            return []

    def get_graph_data(self):
        """Returns graph data in a format suitable for frontend visualization."""
        G = self.get_graph()
        if not G: return {"nodes": [], "edges": []}

        self._calculate_potential_metrics() # Ensure metrics are ready
        nodes = []
        for n, data in G.nodes(data=True):
            nodes.append({
                "id": n,
                "data": { 
                    "label": data["label"], 
                    "yield": data["yield_val"], 
                    "effort": data["effort"],
                    "weakness": data.get("weakness", 0),
                    "roi": round(data.get("roi", 0), 2),
                    "group": data["group"],
                    "musk_category": data.get("musk_category", "FOCUS") # Default to FOCUS if missing
                },
                "position": {"x": 0, "y": 0} 
            })

        edges = []
        for u, v in G.edges():
            edges.append({
                "id": f"e{u}-{v}",
                "source": u,
                "target": v,
                "animated": True
            })

        return {"nodes": nodes, "edges": edges}

    def _calculate_potential_metrics(self):
        """
        Calculates 'potential' yield and effort for each node.
        """
        G = self.get_graph()
        if not G: return

        try:
            topo_order = list(reversed(list(nx.topological_sort(G))))
        except nx.NetworkXUnfeasible:
            return

        for node in topo_order:
            current = G.nodes[node]
            potential_yield = current.get("yield_val", 0)
            potential_effort = current.get("effort", 1)
            
            for successor in G.successors(node):
                succ_node = G.nodes[successor]
                potential_yield += succ_node.get("potential_yield", 0)
                potential_effort += succ_node.get("potential_effort", 0)
            
            G.nodes[node]["potential_yield"] = potential_yield
            G.nodes[node]["potential_effort"] = potential_effort
            roi = potential_yield / potential_effort if potential_effort > 0 else 0
            G.nodes[node]["potential_roi"] = roi
            
            if roi < 0.5:
                category = "DELETE"
            elif roi < 1.5:
                category = "ACCELERATE"
            else:
                category = "FOCUS"
                
            G.nodes[node]["musk_category"] = category

    def calculate_optimal_path(self, time_budget_hours):
        """
        Finds the 'Golden Path' using a Smart Greedy approach.
        """
        self._calculate_potential_metrics()
        G = self.get_graph()
        if not G: return {"path": [], "total_yield": 0, "total_effort": 0, "time_budget": time_budget_hours}

        available_nodes = [n for n, d in G.in_degree() if d == 0]
        completed_nodes = set()
        path = []
        current_time = 0
        
        while current_time < time_budget_hours:
            candidates = []
            for node in available_nodes:
                effort = G.nodes[node]["effort"]
                # Convert effort (0-100 scale) to hours? Let's assume 100 effort = 10 hours for now
                effort_hours = effort / 10.0
                if current_time + effort_hours <= time_budget_hours:
                    candidates.append(node)
            
            if not candidates:
                break
                
            best_node = max(candidates, key=lambda n: (
                G.nodes[n].get("potential_roi", 0),
                G.nodes[n].get("roi", 0)
            ))
            
            path.append(G.nodes[best_node])
            completed_nodes.add(best_node)
            current_time += (G.nodes[best_node]["effort"] / 10.0)
            
            available_nodes.remove(best_node)
            
            for successor in G.successors(best_node):
                if all(pred in completed_nodes for pred in G.predecessors(successor)):
                    available_nodes.append(successor)
                    
        return {
            "path": path,
            "total_yield": sum(item["yield_val"] for item in path),
            "total_effort": sum(item["effort"] for item in path),
            "time_budget": time_budget_hours
        }

golden_path = GoldenPathService()
