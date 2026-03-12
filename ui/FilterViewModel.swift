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
    private struct ProcessConfiguration {
        let executableURL: URL
        let arguments: [String]
        let workingDirectoryURL: URL
        let runtimeDescription: String
    }

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

        let configuration = makeProcessConfiguration()
        addLog("运行环境: \(configuration.runtimeDescription)")

        executeCommand(configuration: configuration)
    }

    private func buildCliArguments() -> [String] {
        [
            "--input", inputFilePath,
            "--keywords", keywords,
            "--mode", matchMode.rawValue,
            "--rule", matchRule.rawValue,
            "--output", outputFilePath,
            "--show-keywords"
        ]
    }

    private func makeProcessConfiguration() -> ProcessConfiguration {
        let cliArguments = buildCliArguments()

        if let bundledBinaryURL = getBundledBinaryURL() {
            return ProcessConfiguration(
                executableURL: bundledBinaryURL,
                arguments: cliArguments,
                workingDirectoryURL: bundledBinaryURL.deletingLastPathComponent(),
                runtimeDescription: "应用内置运行时"
            )
        }

        let projectRoot = resolveProjectRoot()
        return ProcessConfiguration(
            executableURL: URL(fileURLWithPath: "/usr/bin/python3"),
            arguments: ["-m", "core.chat_filter"] + cliArguments,
            workingDirectoryURL: projectRoot,
            runtimeDescription: "系统 Python（开发环境）"
        )
    }

    private func executeCommand(configuration: ProcessConfiguration) {
        let process = Process()
        let outputPipe = Pipe()
        let errorPipe = Pipe()

        self.process = process
        self.outputPipe = outputPipe
        self.errorPipe = errorPipe

        process.executableURL = configuration.executableURL
        process.arguments = configuration.arguments
        process.currentDirectoryURL = configuration.workingDirectoryURL

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
            addLog("错误: 无法启动处理进程 - \(error.localizedDescription)")
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
            errorMessage = "处理进程异常退出，退出码: \(exitCode)"
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

    // MARK: - Runtime Resolution
    private func getBundledBinaryURL() -> URL? {
        guard let executableDirectory = Bundle.main.executableURL?.deletingLastPathComponent() else {
            return nil
        }

        let candidate = executableDirectory
            .appendingPathComponent("ChatFilterBinary", isDirectory: true)
            .appendingPathComponent("ChatFilterBinary", isDirectory: false)

        guard FileManager.default.isExecutableFile(atPath: candidate.path) else {
            return nil
        }

        return candidate
    }

    private func resolveProjectRoot() -> URL {
        if let envRoot = ProcessInfo.processInfo.environment["CHAT_FILTER_PROJECT_ROOT"], !envRoot.isEmpty {
            return URL(fileURLWithPath: envRoot)
        }

        let sourceFileURL = URL(fileURLWithPath: #filePath)
        return sourceFileURL.deletingLastPathComponent().deletingLastPathComponent()
    }
}
