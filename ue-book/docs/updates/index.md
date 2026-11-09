---
title: '2026-11-09 引擎周报'
date: '2026-11-09'
---
# 2026-11-09 引擎周报

## ✨ 新功能
- Wasm：Mac 和 Linux 安装构建现在附带 Wasm 目标平台，由 Win64 游戏编译生成。
- Wasm Memory64：为 lowered Memory64 链接实现 2 GB 以上堆寻址，所有生成的 JS 堆访问及 pipelines 均可正常工作；新增 WasmSmokeHighHeap Node 测试覆盖 2 GB 以上地址。
- Web shader 分发：移动端各 tier 的 shader libraries 和 cold shader groups 独立打包到 IoStore container，由 WebGPU RHI 根据实际运行 tier 挂载和加载；页面改为读取 tier 和 late 标签，不再依赖 chunk 编号。
- Web hosting：游戏文件增加 Cross-Origin-Resource-Policy: cross-origin，允许跨源隔离页面将游戏嵌入 iframe。

## 🚀 重大变更
- UBT：增加构建时拒绝规则，bNoStaticDestructors 仅支持基于 LLVM 20.1 或更高版本的 Clang；bSkipCompilation 模块若可通过名称加载则会被拒绝。
- Wasm 安装引擎：拒绝 Target.cs web 编译设置中无法与预编译引擎模块匹配的选项，并警告仅影响项目代码的 UBT 选项。

## ⚡ 性能优化
- Web：GetMemoryUsedFast 改为无锁读取 heap top。
- Web RHI：采样 back buffer 的 bind groups 在 web 上缓存。
- Web prewarm lists：无法等待的使用在 READY 后立即需要的 pipelines 保留在启动部分；Lyra web 桌面 prewarm list 已针对 Lumen dispatch wraps 重新录制。
- Unreal Canvas：转换缓存导入移至独立的 converter 进程，不再阻塞编辑器。

## 🐛 Bug 修复
- Web GPU bindings：映射用于写入的 buffer range 初始化为零，修正填充长度被误传为结束偏移的问题。
- Web RHI：只读深度或模板的 pass 不再记录 render bundles，因为浏览器忽略 bundle 的只读标志；writable-depth 跟进修复了 multisampled limit warning、WebKit detector、depth copy stats 和 contracts。
- Wasm RHI：draws 仅在更新之前排队的工作完成后绑定流式纹理引用的新 target。
- Web page：无 GPU adapter 时提示硬件加速可能关闭并给出开启方法，而非直接归咎 GPU 或驱动。
- Web page：file:// 打开的页面提示通过服务器提供服务并命名 Play_ launcher，而非显示服务器头卡片。
- Web page：deferred pick 与 forward pick 一样运行 2 个 task-graph workers；移动端两个 tier 均设置 phone worker 上限，Firefox 从 forward 启动，丢失设备时使用 forward fallback，Chromium 版本下限设为 133。
- Web input：Slate 文本框中 Backspace 可正常删除。
- Web：浏览器保持音频挂起时音频 mixer 继续渲染。
- Web：安装引擎会 cook 项目在 NeverCookPluginContent 中列出的插件内容。
- Lyra：语言设置仅列出当前构建可解析的 cultures。
- Web platform：无 vendor 的 adapter 使用 unknown vendor id，避免 vendor 检查断言。
- Wasm UAT：stage 命令删除页面的文件列表，确保 restaged kept stage 始终重新打包。
- Wasm tooling：webdoctor.py 按引擎方式读取容器，并在 Shipping stage 传递正确 host。
- Wasm：FPThreadEvent::Wait 在事件 mutex 外打开任务工作线程的 oversubscription scope。
- Wasm：安装构建为项目挂载 Saved，使存档在重载后保留。
- Wasm：Android pthread pool 调整为 24。
- Wasm：Wasm_ASTC 保持 alpha 和 UI 纹理为 4x4 blocks，增量 cook 能识别其纹理规则。
- Wasm：sky capture shadow extension 从 GetOnPostEngineInit() 创建，不再使用废弃的 OnPostEngineInit。
- Textures：在要求整块 mip 的 RHI 如 WebGPU 上，纹理资源的第一 mip 保持完整 block。
- Mover：用户自定义结构在数据存在期间保持其 struct type 存活。
- Mover：在 Uninit 中释放状态机工作数据，不必等到 C++ 析构。
- Lumen scene direct lighting：对每光源类型的光 tile dispatches 进行 wrap，避免超出 group count 限制。
- Linux：DeleteFile 和 DeleteDirectory 移除符号链接，包括悬空链接。
- Mac：替换 UnrealEditorServices 中废弃的 AppKit API。
- Unreal Canvas Bridge：编辑器退出时若服务器下载进行中，不再崩溃。
- Unreal Canvas converter：先写出 job 的包到磁盘，待 derived-data cache 持有导入构建内容后再应答 job。