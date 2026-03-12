import SwiftUI

struct ContentView: View {
    @StateObject private var viewModel = FilterViewModel()
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            headerView
            
            Divider()
            
            // Main content
            HSplitView {
                // Left panel - Settings
                settingsPanel
                    .frame(minWidth: 280, idealWidth: 320, maxWidth: .infinity)

                // Right panel - Results/Logs
                resultsPanel
                    .frame(minWidth: 400, idealWidth: 500)
            }
        }
        .frame(minWidth: 680, minHeight: 500)
        .alert("错误", isPresented: $viewModel.showError) {
            Button("确定") { }
        } message: {
            Text(viewModel.errorMessage)
        }
    }
    
    // MARK: - Header
    private var headerView: some View {
        HStack {
            Image(systemName: "bubble.left.and.bubble.right.fill")
                .font(.title2)
                .foregroundColor(.blue)
            
            Text("聊天记录筛选导出工具")
                .font(.headline)
            
            Spacer()
            
            if viewModel.isProcessing {
                ProgressView()
                    .scaleEffect(0.7)
                    .padding(.trailing, 8)
                Text("处理中...")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color(NSColor.windowBackgroundColor))
    }
    
    // MARK: - Settings Panel
    private var settingsPanel: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // File Selection
                GroupBox {
                    VStack(alignment: .leading, spacing: 12) {
                        Label("输入文件", systemImage: "doc.badge.arrow.up")
                            .font(.system(size: 13, weight: .semibold))

                        HStack {
                            TextField("选择聊天HTML文件", text: $viewModel.inputFilePath)
                                .textFieldStyle(.roundedBorder)
                                .disabled(true)

                            Button {
                                viewModel.selectInputFile()
                            } label: {
                                Image(systemName: "folder")
                            }
                            .buttonStyle(.bordered)
                            .disabled(viewModel.isProcessing)
                        }
                    }
                    .padding(8)
                }

                // Keywords
                GroupBox {
                    VStack(alignment: .leading, spacing: 12) {
                        Label("关键词", systemImage: "text.magnifyingglass")
                            .font(.system(size: 13, weight: .semibold))

                        TextField("输入关键词，用逗号分隔", text: $viewModel.keywords)
                            .textFieldStyle(.roundedBorder)
                            .disabled(viewModel.isProcessing)

                        Text("例如: 借款, 转账, 红包")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .padding(8)
                }

                // Match Mode
                GroupBox {
                    VStack(alignment: .leading, spacing: 12) {
                        Label("匹配模式", systemImage: "slider.horizontal.3")
                            .font(.system(size: 13, weight: .semibold))

                        Picker("匹配模式", selection: $viewModel.matchMode) {
                            Text("模糊匹配").tag(MatchMode.fuzzy)
                            Text("精确匹配").tag(MatchMode.exact)
                        }
                        .pickerStyle(.segmented)
                        .disabled(viewModel.isProcessing)

                        Text(viewModel.matchMode == .fuzzy ? "模糊匹配: 包含关键词即可" : "精确匹配: 完全等于关键词")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .padding(8)
                }

                // Match Rule
                GroupBox {
                    VStack(alignment: .leading, spacing: 12) {
                        Label("匹配规则", systemImage: "arrow.triangle.branch")
                            .font(.system(size: 13, weight: .semibold))

                        Picker("匹配规则", selection: $viewModel.matchRule) {
                            Text("任意匹配").tag(MatchRule.any)
                            Text("全部匹配").tag(MatchRule.all)
                        }
                        .pickerStyle(.segmented)
                        .disabled(viewModel.isProcessing)

                        Text(viewModel.matchRule == .any ? "任意关键词匹配即可" : "所有关键词都匹配")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    .padding(8)
                }

                // Output Settings
                GroupBox {
                    VStack(alignment: .leading, spacing: 12) {
                        Label("输出文件", systemImage: "square.and.arrow.down")
                            .font(.system(size: 13, weight: .semibold))

                        HStack {
                            TextField("输出文件路径", text: $viewModel.outputFilePath)
                                .textFieldStyle(.roundedBorder)
                                .disabled(true)

                            Button {
                                viewModel.selectOutputFile()
                            } label: {
                                Image(systemName: "folder")
                            }
                            .buttonStyle(.bordered)
                            .disabled(viewModel.isProcessing)
                        }

                        Picker("输出格式", selection: $viewModel.outputFormat) {
                            Text("HTML").tag(OutputFormat.html)
                            Text("PDF").tag(OutputFormat.pdf)
                        }
                        .pickerStyle(.segmented)
                    }
                    .padding(8)
                }

                Spacer()

                // Run Button
                Button {
                    viewModel.runFilter()
                } label: {
                    HStack {
                        Image(systemName: "play.fill")
                        Text("开始筛选")
                    }
                    .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)
                .disabled(viewModel.isProcessing || !viewModel.canRun)

                if !viewModel.canRun && !viewModel.isProcessing {
                    Text("请选择输入文件、输入关键词和输出文件")
                        .font(.caption)
                        .foregroundColor(.orange)
                }
            }
            .padding()
        }
    }
    
    // MARK: - Results Panel
    private var resultsPanel: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Results header
            HStack {
                Label("执行日志", systemImage: "terminal")
                    .font(.system(size: 13, weight: .semibold))
                
                Spacer()
                
                Button {
                    viewModel.clearLogs()
                } label: {
                    Image(systemName: "trash")
                }
                .buttonStyle(.borderless)
                .disabled(viewModel.logs.isEmpty || viewModel.isProcessing)
            }
            .padding()
            .background(Color(NSColor.controlBackgroundColor))
            
            Divider()
            
            // Logs
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 4) {
                        ForEach(Array(viewModel.logs.enumerated()), id: \.offset) { index, log in
                            Text(log)
                                .font(.system(.body, design: .monospaced))
                                .foregroundColor(logColor(for: log))
                                .id(index)
                                .textSelection(.enabled)
                        }
                    }
                    .padding()
                }
                .background(Color(NSColor.textBackgroundColor))
                .onChange(of: viewModel.logs.count) { _ in
                    if let lastIndex = viewModel.logs.indices.last {
                        withAnimation {
                            proxy.scrollTo(lastIndex, anchor: .bottom)
                        }
                    }
                }
            }
            
            // Summary
            if viewModel.isCompleted {
                Divider()
                summaryView
            }
        }
    }
    
    // MARK: - Summary View
    private var summaryView: some View {
        HStack(spacing: 20) {
            SummaryItem(
                icon: "doc.text",
                title: "总消息",
                value: "\(viewModel.totalMessages)",
                color: .blue
            )
            
            SummaryItem(
                icon: "checkmark.circle",
                title: "匹配消息",
                value: "\(viewModel.matchedMessages)",
                color: .green
            )
            
            SummaryItem(
                icon: "arrow.right.doc",
                title: "输出文件",
                value: viewModel.outputFileName,
                color: .orange
            )
            
            Spacer()
            
            Button {
                NSWorkspace.shared.selectFile(viewModel.outputFilePath, inFileViewerRootedAtPath: "")
            } label: {
                Label("在Finder中显示", systemImage: "folder")
            }
            .buttonStyle(.bordered)
        }
        .padding()
        .background(Color(NSColor.controlBackgroundColor))
    }
    
    private func logColor(for log: String) -> Color {
        if log.contains("错误") || log.contains("Error") || log.contains("失败") {
            return .red
        } else if log.contains("PROGRESS:") {
            return .blue
        } else if log.contains("完成") || log.contains("完成!") {
            return .green
        } else if log.contains("警告") || log.contains("Warning") {
            return .orange
        }
        return .primary
    }
}

// MARK: - Summary Item
struct SummaryItem: View {
    let icon: String
    let title: String
    let value: String
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack(spacing: 4) {
                Image(systemName: icon)
                    .foregroundColor(color)
                Text(title)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            Text(value)
                .font(.headline)
                .lineLimit(1)
        }
    }
}
