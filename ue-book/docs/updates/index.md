---
title: '2026-06-02 引擎周报'
date: '2026-06-02'
---

# 2026-06-02 引擎周报

## ✨ 新功能
- **Niagara**: 添加了内部插件，支持将发射器转换为轻量级版本，并提供了相应的 API 变更。
- **RHI 设备分析**: 实现了 RHI 设备分析提供程序，用于收集设备相关的分析数据。
- **EDA/工具集**: 在 EditorAppToolset、GameplayTagsToolset 和 Python AssetTools 中统一了所有返回资产路径的 AICallable 函数，使其输出格式一致，便于与其他工具流水线连接。
- **游戏输入**: 重组了 Game Input NuGet 的位置，以优化模块管理。
- **输入与应用**: 将 IInputDevice 模块的注册和创建整合到 GenericApplication 层中，简化了输入设备的管理。
- **EQS**: 添加了“方向点”（oriented point）项目类型，增强了环境查询系统的能力。
- **PCG**: 为运行时生成调度器的流式查询添加了数据层和EDL支持。
- **应用内评测**: 通过 Google Play Review API 为 Android 添加了应用内商店评测支持。
- **控制绑定**: 将 UControlRigBlueprintGeneratedClass 包含在内容浏览器过滤器中，确保经过烘焙的 Control Rig 资产不会被过滤掉。
- **Verse**: 防止当覆盖项已提供默认值时，Verse 仍然报告缺失默认值的 3600 错误。

## 🚀 重大变更
- **算法**: 重构了 `Algo::ParallelDeterministicSort`，使其在不同 worker 数量的机器上都能产生确定性结果。工作块数量现在仅取决于范围大小，分区、归约树形状和累积器在运行间保持一致，确保跨机器的确定性排序。
- **渲染**: 将 Gaussian Splat 管道迁移到 GPU 驱动模式，以提升渲染性能和扩展性。

## ⚡ 性能优化
- **Prefab 编辑器**: 在大纲视图中为简单控件启用了 Slate 动态失效机制，以优化 UI 更新性能。
- **GPU 排序**: 扩展了 GPU Radix Sort 以处理间接派发（Indirect Dispatch），并将其添加到自动化测试套件中。
- **Outliner**: 对 TEDS Outliner 进行了优化，将新增行合并后执行一次排序节点更新，而非对每次添加都进行更新。
- **材质接口**: 避免了在非必要情况下为每个 UMaterialInterface 创建读写锁（RWLock）原语，减少了不必要的开销。
- **导航系统**: 增加了在记录导航路径时更改日志类别和颜色的能力，有助于更精细的性能分析和调试。

## 🐛 Bug 修复
- **几何体集合**: 修复了 Geometry Collection Renderable 无法正确渲染颜色属性的问题。
- **控制绑定**: 在 ControlRig.cpp 中修复了对 WorldTransformDS 进行空值检查后再解引用的崩溃风险。
- **Niagara**: 修复了 SKM DI（Skeletal Mesh Data Interface）中由于使用已释放的蒙皮权重缓冲区（skin weight buffers）导致的崩溃（use-after-free）问题。
- **渲染 (VulkanRHI)**: 当 NumFramesToWaitForResourceDelete 设置为 0 时，改用常规延迟删除而非专用 UB 系统，并创建了专用 CVar 来控制描述符在缓存中的保留时间，修复了桌面端 Vulkan 的 SM5 问题。
- **控制绑定/UAF**: 修复了在 PIE 运行时通过细节面板编辑带有 MoverComponent 的 Actor 属性导致的崩溃和陈旧对象映射问题。现在会销毁并重新创建移动模拟。
- **材质编辑器**: 修复了新材质翻译器在材质中已删除的参数位于已修剪的 MaterialAttributes 插槽下时，对复合体（Composite）进行 MIR 检查失败的问题。
- **远程对象 (RemoteObjects)**: 修复了迁移具有链接动画节点的 UAnimInstance 的问题；修复了在序列化过程中尝试解引用 TObjectPtr 可能导致非法迁移的问题；为 UAbilityTask 添加了 PostMigrate 逻辑以处理能力计数。
- **动画节点**: 修复了 `FMeshWeights::CotanCentroidSafe` 退化回退未使用传入的 PositionFunc 的问题。
- **Slate/滚动框**: 修复了在某些平台的测试/发布版本中，带有自定义导航设置的 ScrollBox 控件可能强制将子控件大小设为 0 的边缘情况。
- **网络测试**: 修复了自动化测试中 YieldBoundary 的替换问题，确保了 LatentIt/LatentBeforeEach 的正确执行顺序。
- **GPU Profiler**: 在 CSV Profiler 的 GPU 分解中，将 GPUSkinCache 和 SubmitBufferUploads 从未计入（Unaccounted）类别中分离出来。
- **编译器**: 修复了着色器预处理器在处理没有固定参数的可变参数宏时的断言失败问题。
- **PCG**: 修复了自定义 HLSL 内核源代码中的非 ASCII 空白字符标准化问题；修复了默认点种子值被设置为 0 而非 42 的问题；修复了批量复制 MetaSound 时的烘焙依赖错误；修复了保存 RGBA 浮点纹理到资产时 Alpha 通道丢失的问题。
- **动画**: 为动画节点运行时添加了对作用域类型（scoped types）的支持。
- **输入**: 修复了游戏输入中的调用频率设置问题。
- **Verse**: 防止了在序列化过程中尝试解引用 TObjectPtr 可能导致的非法迁移。
- **BPI**: 修复了在工具提示准备期间解引用 FNodeTextCache schema 时空指针导致的崩溃。
- **物理**: 添加了一个内部的物理重叠查询函数，用于在物理线程上运行。
- **动画**: 为动画节点运行时添加了对作用域类型（scoped types）的支持。
- **Horde**: 修复了当 unshelve 没有可操作文件时 PerforceMaterializer 的脏状态标记问题。
- **Trace**: 修复了 Trace Trimmer 和 Trace Query 中的格式说明符警告。
- **MetaSound**: 在编辑器中禁用了 MetaSound 自动操作缓存，防止正在编辑的 MetaSound 被错误缓存。
- **动画绑定**: 修复了动画绑定进入错误状态的问题。
- **云 DDC**: 启用了默认的启动探测（startup probe），以减轻在使用数据存储（Data Store）时的启动压力。

## 🔧 API 变更
- **对话系统**: 将 EConversationUpdateType 转换为一个蓝图暴露的 UENUM，并将 FWebApplication& 传递给 FOnConversationUpdated 订阅者。
- **分析接口**: 在 IAnalyticsProviderET 接口中添加了 AddOrUpdateDefaultValue 函数，用于添加或更新单个属性值，避免了复制和更新整个属性数组的开销。
- **程序目标**: 为程序添加了 bAllowEngineStdioOutput 目标规则，允许拥有自己的标准输出/错误流。
- **Web 应用程序**: WithWebApplication 函数现在返回一个 bool 值，指示回调是否已执行。
- **物理**: 添加了一个内部的物理重叠查询函数，用于在物理线程上运行。
- **Android UPL**: 添加了 additionalJavaSrcDirs 节点，以支持在 Gradle 中直接使用模块的 Java 文件。
- **构建**: 启用了针对非 P4 仓库的 UE 版本标记逻辑。