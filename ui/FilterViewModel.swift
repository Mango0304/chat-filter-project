import Foundation
import SwiftUI
import Combine

// MARK: - Enums
enum MatchMode: String, CaseIterable {
    case fuzzy = "fuzzy"
    case exact = "exact"
}

enum MatchRule: String, CaseIterable {
    case any = "any"
    case all = "all"
}

enum OutputFormat: String, CaseIterable {
    case html = "html"
    case pdf = "pdf"
}

// MARK: - FilterViewModel
@MainActor
class FilterViewModel: ObservableObject {
    // MARK: - Published Properties
    @Published var inputFilePath: String = ""
    @Published var keywords: String = ""
    @Published var matchMode: MatchMode = .fuzzy
    @Published var matchRule: MatchRule = .any
    @Published var outputFilePath: String = ""
    @Published var outputFormat: OutputFormat = .html {
        didSet {
            // 当输出格式改变时，自动更新文件扩展名
            if !outputFilePath.isEmpty {
                let url = URL(fileURLWithPath: outputFilePath)
                let directory = url.deletingLastPathComponent().path
                let baseName = url.deletingPathExtension().lastPathComponent
                outputFilePath = "\(directory)/\(baseName).\(outputFormat.rawValue)"
            }
        }
    }
    
    @Published var isProcessing: Bool = false
    @Published var isCompleted: Bool = false
    @Published var showError: Bool = false
    @Published var errorMessage: String = ""
    
    @Published var logs: [String] = []
    @Published var totalMessages: Int = 0
    @Published var matchedMessages: Int = 0
    
    // MARK: - Private Properties
    private var process: Process?
    private var outputPipe: Pipe?
    private var errorPipe: Pipe?
    
    // MARK: - Computed Properties
    var canRun: Bool {
        !inputFilePath.isEmpty && !keywords.isEmpty && !outputFilePath.isEmpty
    }
    
    var outputFileName: String {
        URL(fileURLWithPath: outputFilePath).lastPathComponent
    }
    
    // MARK: - File Selection
    func selectInputFile() {
        let panel = NSOpenPanel()
        panel.title = "选择聊天记录HTML文件"
        panel.allowedContentTypes = [.html]
        panel.allowsMultipleSelection = false
        panel.canChooseDirectories = false
        panel.canChooseFiles = true
        panel.message = "请选择导出的聊天记录HTML文件"
        
        if panel.runModal() == .OK, let url = panel.url {
            inputFilePath = url.path
            
            // Auto-set output file if not set
            if outputFilePath.isEmpty {
                let baseName = url.deletingPathExtension().lastPathComponent
                let outputDir = url.deletingLastPathComponent().path
                let ext = outputFormat.rawValue
                outputFilePath = "\(outputDir)/\(baseName)_filtered.\(ext)"
            }
        }
    }
    
    func selectOutputFile() {
        let panel = NSSavePanel()
        panel.title = "选择输出文件"
        panel.allowedContentTypes = outputFormat == .html ? [.html] : [.pdf]
        panel.canCreateDirectories = true
        panel.nameFieldStringValue = generateDefaultOutputName()
        
        if panel.runModal() == .OK, let url = panel.url {
            outputFilePath = url.path
        }
    }
    
    private func generateDefaultOutputName() -> String {
        if !inputFilePath.isEmpty {
            let baseName = URL(fileURLWithPath: inputFilePath).deletingPathExtension().lastPathComponent
            return "\(baseName)_filtered.\(outputFormat.rawValue)"
        }
        return "chat_filtered.\(outputFormat.rawValue)"
    }
    
    // MARK: - Run Filter
    func runFilter() {
        guard canRun else { return }
        
        isProcessing = true
        isCompleted = false
        logs = []
        totalMessages = 0
        matchedMessages = 0
        
        addLog("开始筛选聊天记录...")
        addLog("输入文件: \(inputFilePath)")
        addLog("关键词: \(keywords)")
        addLog("匹配模式: \(matchMode.rawValue), 匹配规则: \(matchRule.rawValue)")
        addLog("输出文件: \(outputFilePath)")
        addLog("---")
        
        // Build command arguments
        let args = buildArguments()
        
        // Execute Python command
        executePythonCommand(arguments: args)
    }
    
    private func buildArguments() -> [String] {
        var args: [String] = []
        
        args.append("-m")
        args.append("core.chat_filter")
        args.append("--input")
        args.append(inputFilePath)
        args.append("--keywords")
        args.append(keywords)
        args.append("--mode")
        args.append(matchMode.rawValue)
        args.append("--rule")
        args.append(matchRule.rawValue)
        args.append("--output")
        args.append(outputFilePath)
        args.append("--show-keywords")
        
        return args
    }
    
    private func executePythonCommand(arguments: [String]) {
        let process = Process()
        let outputPipe = Pipe()
        let errorPipe = Pipe()

        self.process = process
        self.outputPipe = outputPipe
        self.errorPipe = errorPipe

        // 判断是否在打包环境中运行
        if let bundledInfo = getBundledPythonInfo() {
            // 打包环境：使用打包的 Python + 正确的工作目录
            process.executableURL = URL(fileURLWithPath: bundledInfo.pythonPath)
            process.currentDirectoryURL = URL(fileURLWithPath: bundledInfo.workingDir)
            // 使用原始参数 -m core.chat_filter
            process.arguments = arguments
        } else {
            // 开发环境：使用系统Python
            process.executableURL = URL(fileURLWithPath: "/usr/bin/python3")
            process.arguments = arguments
            
            // 动态获取项目根目录（支持开发和打包环境）
            let projectRoot: URL
            let mainBundlePath = Bundle.main.bundlePath
            if mainBundlePath.hasSuffix(".app") {
                // 打包环境：从 app 位置推断项目目录
                // /path/to/AppName.app/Contents/MacOS/xxx -> /path/to/
                let appURL = URL(fileURLWithPath: mainBundlePath)
                let contentsURL = appURL.deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
                projectRoot = contentsURL
            } else {
                // Xcode开发环境：优先读取环境变量，否则基于当前源文件路径推断仓库根目录
                if let envRoot = ProcessInfo.processInfo.environment["CHAT_FILTER_PROJECT_ROOT"], !envRoot.isEmpty {
                    projectRoot = URL(fileURLWithPath: envRoot)
                } else {
                    let sourceFileURL = URL(fileURLWithPath: #filePath)
                    projectRoot = sourceFileURL.deletingLastPathComponent().deletingLastPathComponent()
                }
            }
            process.currentDirectoryURL = projectRoot
        }

        process.standardOutput = outputPipe
        process.standardError = errorPipe
        
        // Handle output
        outputPipe.fileHandleForReading.readabilityHandler = { [weak self] handle in
            let data = handle.availableData
            if let output = String(data: data, encoding: .utf8), !output.isEmpty {
                Task { @MainActor in
                    self?.handleOutput(output)
                }
            }
        }
        
        errorPipe.fileHandleForReading.readabilityHandler = { [weak self] handle in
            let data = handle.availableData
            if let output = String(data: data, encoding: .utf8), !output.isEmpty {
                Task { @MainActor in
                    self?.addLog("错误: \(output)")
                }
            }
        }
        
        process.terminationHandler = { [weak self] process in
            Task { @MainActor in
                self?.handleProcessTermination(exitCode: process.terminationStatus)
            }
        }
        
        do {
            try process.run()
        } catch {
            addLog("错误: 无法启动Python进程 - \(error.localizedDescription)")
            isProcessing = false
        }
    }
    
    private func handleOutput(_ output: String) {
        let lines = output.components(separatedBy: "\n")
        for line in lines where !line.isEmpty {
            if line.hasPrefix("PROGRESS:") {
                let progressMessage = String(line.dropFirst("PROGRESS:".count)).trimmingCharacters(in: .whitespaces)
                addLog(progressMessage)
                
                // Parse progress messages
                parseProgressMessage(progressMessage)
            } else {
                // Final output path
                if line.contains("结果已保存到:") {
                    let path = line.replacingOccurrences(of: "结果已保存到:", with: "").trimmingCharacters(in: .whitespaces)
                    addLog("输出文件: \(path)")
                } else if !line.hasPrefix("结果已保存") {
                    addLog(line)
                }
            }
        }
    }
    
    private func parseProgressMessage(_ message: String) {
        // Parse total messages
        if message.contains("共解析") && message.contains("条消息") {
            if let number = extractNumber(from: message) {
                totalMessages = number
            }
        }
        
        // Parse matched messages
        if message.contains("匹配到") && message.contains("条消息") {
            if let number = extractNumber(from: message) {
                matchedMessages = number
            }
        }
        
        // Parse filtered result
        if message.contains("完成!") && message.contains("/") {
            let parts = message.components(separatedBy: " ")
            for (index, part) in parts.enumerated() {
                if part.contains("筛选") && index + 1 < parts.count {
                    let resultPart = parts[index + 1]
                    let numbers = resultPart.components(separatedBy: "/")
                    if numbers.count == 2 {
                        if let matched = Int(numbers[0]) {
                            matchedMessages = matched
                        }
                        if let total = Int(numbers[1]) {
                            totalMessages = total
                        }
                    }
                    break
                }
            }
        }
    }
    
    private func extractNumber(from string: String) -> Int? {
        let digits = string.compactMap { $0.wholeNumberValue }
        if digits.isEmpty { return nil }
        return Int(digits.map { String($0) }.joined())
    }
    
    private func handleProcessTermination(exitCode: Int32) {
        outputPipe?.fileHandleForReading.readabilityHandler = nil
        errorPipe?.fileHandleForReading.readabilityHandler = nil
        
        isProcessing = false
        
        if exitCode == 0 {
            isCompleted = true
            addLog("---")
            addLog("筛选完成!")
        } else {
            addLog("---")
            addLog("筛选失败，退出码: \(exitCode)")
            errorMessage = "Python进程异常退出，退出码: \(exitCode)"
            showError = true
        }
        
        process = nil
        outputPipe = nil
        errorPipe = nil
    }
    
    // MARK: - Log Management
    func addLog(_ message: String) {
        let timestamp = DateFormatter.localizedString(from: Date(), dateStyle: .none, timeStyle: .medium)
        logs.append("[\(timestamp)] \(message)")
    }
    
    func clearLogs() {
        logs = []
        isCompleted = false
    }

    // MARK: - Bundled Python Detection
    private func getBundledPythonInfo() -> (pythonPath: String, workingDir: String)? {
        // 检测是否在Xcode打包环境中运行
        let envVars = ProcessInfo.processInfo.environment
        
        // 方法1: 检查Bundle路径（打包后的 app）
        if let bundlePath = Bundle.main.bundlePath as NSString?, bundlePath.pathExtension == "app" {
            let appDir = bundlePath.deletingLastPathComponent
            let macOSPath = (appDir as NSString).deletingLastPathComponent
            let resourcesPath = (macOSPath as NSString).deletingLastPathComponent
            
            // 检查 _internal/Python3.framework 打包的 Python
            let pythonFrameworkPath = "\(resourcesPath)/Contents/Resources/_internal/Python3.framework/Versions/3.9/Python3"
            let internalPath = "\(resourcesPath)/Contents/Resources/_internal"
            
            if FileManager.default.fileExists(atPath: pythonFrameworkPath) {
                // 使用打包的 Python + _internal 作为工作目录
                return (pythonPath: pythonFrameworkPath, workingDir: internalPath)
            }
            
            // 也检查 Contents/MacOS 下的启动器
            let launcherPath = "\(appDir)/Contents/MacOS/ChatFilter"
            if FileManager.default.fileExists(atPath: launcherPath) {
                return (pythonPath: launcherPath, workingDir: resourcesPath + "/Contents/Resources")
            }
        }

        // 方法2: 检查是否是直接运行打包的二进制
        let executablePath = CommandLine.arguments[0]
        if executablePath.contains("ChatFilterBinary") || executablePath.contains("ChatFilter.app") {
            let appDir = (executablePath as NSString).deletingLastPathComponent
            let resourcesPath = (appDir as NSString).deletingLastPathComponent
            let internalPath = "\(resourcesPath)/Contents/Resources/_internal"
            
            if FileManager.default.fileExists(atPath: internalPath) {
                let pythonPath = "\(internalPath)/Python3.framework/Versions/3.9/Python3"
                if FileManager.default.fileExists(atPath: pythonPath) {
                    return (pythonPath: pythonPath, workingDir: internalPath)
                }
            }
        }

        // 方法3: Xcode 开发环境
        if envVars["XCODE_RUNNING"] != nil || envVars["XPC_SERVICE_NAME"] != nil {
            if let productDir = envVars["BUILT_PRODUCTS_DIR"] {
                let xcodePath = "\(productDir)/ChatFilter.app/Contents/MacOS/ChatFilter"
                if FileManager.default.fileExists(atPath: xcodePath) {
                    return (pythonPath: xcodePath, workingDir: productDir)
                }
            }
        }

        return nil
    }
}
