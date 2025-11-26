# Backend API Testing Script
# Tests all major API endpoints and logs results

$baseUrl = "http://localhost:5000"
$results = @()

function Test-API {
    param($method, $endpoint, $body = $null, $testName)
    
    Write-Host "`n=== Testing: $testName ===" -ForegroundColor Cyan
    Write-Host "Method: $method | Endpoint: $endpoint" -ForegroundColor Gray
    
    try {
        $params = @{
            Uri = "$baseUrl$endpoint"
            Method = $method
            UseBasicParsing = $true
        }
        
        if ($body) {
            $params.Body = ($body | ConvertTo-Json)
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-WebRequest @params
        $content = $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
        
        Write-Host "✓ PASS - Status: $($response.StatusCode)" -ForegroundColor Green
        Write-Host "Response: $content" -ForegroundColor White
        
        $results += [PSCustomObject]@{
            Test = $testName
            Status = "PASS"
            StatusCode = $response.StatusCode
            Response = $content
        }
    }
    catch {
        Write-Host "✗ FAIL - Error: $($_.Exception.Message)" -ForegroundColor Red
        
        $results += [PSCustomObject]@{
            Test = $testName
            Status = "FAIL"
            StatusCode = if ($_.Exception.Response.StatusCode.value__) { $_.Exception.Response.StatusCode.value__ } else { "N/A" }
            Error = $_.Exception.Message
        }
    }
}

# ===== ANALYTICS APIs =====
Write-Host "`n╔════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║  ANALYTICS API TESTS          ║" -ForegroundColor Yellow
Write-Host "╚════════════════════════════════╝" -ForegroundColor Yellow

Test-API "GET" "/api/analytics/overview?timeframe=all" -testName "TC-API-014: Get analytics overview"
Test-API "GET" "/api/analytics/overview?timeframe=week" -testName "TC-API-014b: Get weekly analytics"
Test-API "GET" "/api/analytics/subject/Polity" -testName "TC-API-015: Get subject analytics (valid)"
Test-API "GET" "/api/analytics/subject/InvalidSubject" -testName "TC-API-015b: Get subject analytics (invalid)"

# ===== SYLLABUS APIs =====
Write-Host "`n╔════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║  SYLLABUS API TESTS           ║" -ForegroundColor Yellow
Write-Host "╚════════════════════════════════╝" -ForegroundColor Yellow

Test-API "GET" "/api/syllabus/" -testName "TC-API-016: Get all syllabus topics"
Test-API "GET" "/api/syllabus/analytics" -testName "TC-API-016b: Get syllabus analytics"

# Test status update (using ID 1 as example)
$statusUpdate = @{ status = "Reading" }
Test-API "POST" "/api/syllabus/1/status" -body $statusUpdate -testName "TC-API-017: Update topic status"

# Test notes update
$notesUpdate = @{ notes = "Test notes for topic" }
Test-API "POST" "/api/syllabus/1/notes" -body $notesUpdate -testName "TC-API-018: Save topic notes"

# Test revision
Test-API "POST" "/api/syllabus/1/revise" -testName "TC-API-018b: Mark topic as revised"

# ===== WAR MAP APIs =====
Write-Host "`n╔════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║  WAR MAP API TESTS            ║" -ForegroundColor Yellow
Write-Host "╚════════════════════════════════╝" -ForegroundColor Yellow

$today = Get-Date -Format "yyyy-MM-dd"
Test-API "GET" "/api/warmap/tasks?date=$today" -testName "TC-API-003: Get tasks for today"
Test-API "GET" "/api/warmap/status" -testName "TC-API-006b: Get Google Calendar status"

# Create new task
$newTask = @{
    title = "Test Task from API"
    description = "Testing task creation"
    date = $today
    completed = $false
}
Test-API "POST" "/api/warmap/tasks" -body $newTask -testName "TC-API-004: Create new task (positive)"

# Create invalid task (missing title)
$invalidTask = @{
    description = "Task without title"
    date = $today
}
Test-API "POST" "/api/warmap/tasks" -body $invalidTask -testName "TC-API-005: Create task without title (negative)"

# ===== RAVENS APIs =====
Write-Host "`n╔════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║  RAVENS API TESTS             ║" -ForegroundColor Yellow
Write-Host "╚════════════════════════════════╝" -ForegroundColor Yellow

Test-API "GET" "/api/ravens/articles" -testName "TC-API-009: Get articles list"
Test-API "POST" "/api/ravens/bookmark/1" -testName "TC-API-010: Bookmark article"

# ===== ARENA APIs =====
Write-Host "`n╔════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║  ARENA API TESTS              ║" -ForegroundColor Yellow
Write-Host "╚════════════════════════════════╝" -ForegroundColor Yellow

Test-API "GET" "/api/arena/bosses" -testName "TC-API-011: Get all bosses"
Test-API "GET" "/api/arena/bosses/year" -testName "TC-API-011b: Get year bosses"
Test-API "GET" "/api/arena/bosses/subject" -testName "TC-API-011c: Get subject bosses"
Test-API "GET" "/api/arena/bosses/custom" -testName "TC-API-011d: Get custom bosses"
Test-API "GET" "/api/arena/boss/1/questions" -testName "TC-API-012: Get boss questions"

# ===== FLASHCARD APIs =====
Write-Host "`n╔════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║  FLASHCARD API TESTS          ║" -ForegroundColor Yellow
Write-Host "╚════════════════════════════════╝" -ForegroundColor Yellow

Test-API "GET" "/api/flashcards/decks" -testName "TC-API-019b: Get all decks"

# Create new deck
$newDeck = @{ name = "Test Deck API" }
Test-API "POST" "/api/flashcards/decks" -body $newDeck -testName "TC-API-019: Create new deck (positive)"

# Create deck without name
$invalidDeck = @{ name = "" }
Test-API "POST" "/api/flashcards/decks" -body $invalidDeck -testName "TC-API-019c: Create deck without name (negative)"

# ===== REVISION APIs =====
Write-Host "`n╔════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║  REVISION API TESTS           ║" -ForegroundColor Yellow
Write-Host "╚════════════════════════════════╝" -ForegroundColor Yellow

Test-API "GET" "/api/revision/cards" -testName "TC-API-023: Get all revision cards"

# Create revision card
$newCard = @{
    title = "Preamble of Indian Constitution"
    content = "The Preamble of the Constitution is the soul of the Constitution"
}
Test-API "POST" "/api/revision/one-liner" -body $newCard -testName "TC-API-022: Generate revision card (positive)"

# Create without title
$invalidCard = @{ content = "Content without title" }
Test-API "POST" "/api/revision/one-liner" -body $invalidCard -testName "TC-API-022b: Generate card without title (negative)"

# ===== PYQ APIs =====
Write-Host "`n╔════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║  PYQ API TESTS                ║" -ForegroundColor Yellow
Write-Host "╚════════════════════════════════╝" -ForegroundColor Yellow

Test-API "GET" "/api/pyq/questions?year=2024" -testName "TC-API-024: Get PYQ by year"
Test-API "GET" "/api/pyq/questions?subject=Polity" -testName "TC-API-025: Get PYQ by subject"

# ===== SUMMARY =====
Write-Host "`n╔════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║  TEST SUMMARY                  ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════╝" -ForegroundColor Magenta

$totalTests = $results.Count
$passedTests = ($results | Where-Object { $_.Status -eq "PASS" }).Count
$failedTests = ($results | Where-Object { $_.Status -eq "FAIL" }).Count
$passRate = [math]::Round(($passedTests / $totalTests) * 100, 2)

Write-Host "`nTotal Tests: $totalTests" -ForegroundColor White
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Failed: $failedTests" -ForegroundColor Red
Write-Host "Pass Rate: $passRate%" -ForegroundColor $(if ($passRate -ge 80) { "Green" } else { "Yellow" })

# Export results to JSON
$results | ConvertTo-Json -Depth 10 | Out-File "api_test_results.json"
Write-Host "`nDetailed results saved to: api_test_results.json" -ForegroundColor Cyan
