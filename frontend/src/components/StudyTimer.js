"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
var react_1 = require("react");
require("./RitualsPanel.css"); // Reuse existing styles or add new ones
var GlobalContext_1 = require("../contexts/GlobalContext");
var config_1 = require("../config");
var Toast_1 = require("./Toast");
var StudyTimer = function () {
    var refreshDashboard = (0, GlobalContext_1.useGlobal)().refreshDashboard;
    var _a = (0, Toast_1.useToast)(), toasts = _a.toasts, addToast = _a.addToast, removeToast = _a.removeToast;
    var _b = (0, react_1.useState)(0), seconds = _b[0], setSeconds = _b[1];
    var _c = (0, react_1.useState)(false), isActive = _c[0], setIsActive = _c[1];
    var _d = (0, react_1.useState)(false), isPaused = _d[0], setIsPaused = _d[1];
    var intervalRef = (0, react_1.useRef)(null);
    (0, react_1.useEffect)(function () {
        if (isActive && !isPaused) {
            intervalRef.current = setInterval(function () {
                setSeconds(function (s) { return s + 1; });
            }, 1000);
        }
        else {
            if (intervalRef.current)
                clearInterval(intervalRef.current);
        }
        return function () {
            if (intervalRef.current)
                clearInterval(intervalRef.current);
        };
    }, [isActive, isPaused]);
    var handleStart = function () {
        setIsActive(true);
        setIsPaused(false);
    };
    var handlePause = function () {
        setIsPaused(true);
    };
    var handleStop = function () { return __awaiter(void 0, void 0, void 0, function () {
        var minutes, res, data, err_1;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    setIsActive(false);
                    setIsPaused(false);
                    if (seconds < 60) {
                        addToast("Session too short to log (min 1 minute).", "warning");
                        setSeconds(0);
                        return [2 /*return*/];
                    }
                    minutes = Math.floor(seconds / 60);
                    _a.label = 1;
                case 1:
                    _a.trys.push([1, 7, , 8]);
                    return [4 /*yield*/, fetch("".concat(config_1.API_BASE_URL, "/api/tasks/log-study"), {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ minutes: minutes })
                        })];
                case 2:
                    res = _a.sent();
                    if (!res.ok) return [3 /*break*/, 5];
                    return [4 /*yield*/, res.json()];
                case 3:
                    data = _a.sent();
                    addToast("Study session logged! +".concat(data.xp_earned, " XP"), "success");
                    return [4 /*yield*/, refreshDashboard()];
                case 4:
                    _a.sent();
                    return [3 /*break*/, 6];
                case 5:
                    addToast("Failed to log study session.", "error");
                    _a.label = 6;
                case 6: return [3 /*break*/, 8];
                case 7:
                    err_1 = _a.sent();
                    console.error('Error logging study:', err_1);
                    addToast("Error connecting to server.", "error");
                    return [3 /*break*/, 8];
                case 8:
                    setSeconds(0);
                    return [2 /*return*/];
            }
        });
    }); };
    var formatTime = function (totalSeconds) {
        var h = Math.floor(totalSeconds / 3600);
        var m = Math.floor((totalSeconds % 3600) / 60);
        var s = totalSeconds % 60;
        return "".concat(h.toString().padStart(2, '0'), ":").concat(m.toString().padStart(2, '0'), ":").concat(s.toString().padStart(2, '0'));
    };
    return (<div className="study-timer">
            <Toast_1.ToastContainer toasts={toasts} removeToast={removeToast}/>
            <h3>⏱️ Focus Timer</h3>
            <div className="timer-display">{formatTime(seconds)}</div>
            <div className="timer-controls">
                {!isActive ? (<button className="timer-btn start" onClick={handleStart} aria-label="Start study timer">
                        START
                    </button>) : (<>
                        {isPaused ? (<button className="timer-btn resume" onClick={handleStart} aria-label="Resume study timer">
                                RESUME
                            </button>) : (<button className="timer-btn pause" onClick={handlePause} aria-label="Pause study timer">
                                PAUSE
                            </button>)}
                        <button className="timer-btn stop" onClick={handleStop} aria-label="Finish study session and log time">
                            FINISH
                        </button>
                    </>)}
            </div>
        </div>);
};
exports.default = StudyTimer;
