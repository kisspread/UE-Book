---
title: '2026-10-12 引擎周报'
date: '2026-10-12'
---

# 2026-10-12 引擎周报

## ✨ 新功能
- 合并了 UE6 Main 的 Gaussian Splat 工作至 UE5 Main（共 7 个批次），引入/更新 Gaussian Splat 渲染与编辑支持。
- UAF：新增从资产引用播放 Layer Stack 的能力；为所有 UAF Workspace 资产类型提供视口预览；新增可在代码中构建 Node Description Tree 的资产；层内容有效性变化时自动淡入淡出；Slot 驱动的基础层允许使用 Override Asset Slot 层；Layer Stack 已注册到 Anim Node Factory。
- AnimMixer：Mixer Tree 的逐帧值现在可绑定到 UAF 变量，并能从系统资产解析 UAF target 路由（无其他路由时接管系统输出）。
- Chooser：UChooserTable 和 UProxyAsset 现在可引用共享的 UChooserSignature 资产；随机化 Chooser 上下文结构体已暴露给 UAF。
- Control Rig：新增知识库模块及节点目录；Anim Sequence Bake To Control Rig 使用与 Sequencer 一致的 Rig Picker；Double 变量支持映射到 Anim Curves；Modular Rig 变量支持 Verse 往返；Collapse All Layers 采用共享代码自顶向下合并区段，并新增“从选中轨道创建 Anim Layers”选项；Sequencer 支持复制粘贴 Space Channels。
- RewindDebugger：预览网格与动画类改为异步加载。
- Nanite 半透明：支持前层渲染、编辑器选择与拾取，且无 Splat 时无 AVBOIT 开销。

## 🚀 重大变更
- UAF Runtime：移除了 Inline Anim Node 支持，使用内联节点的项目需迁移到外部节点资产。

## ⚡ 性能优化
- RigVM 多项优化：cook 编译去重、图验证/内联缓存、AST 代理指针哈希、ClearInvalidReferences 提前返回。
- UAF Anim Node 销毁拆分为两个阶段，降低单次销毁集中开销。
- RewindDebugger 预览网格和动画类异步加载，减少编辑器阻塞。
- Nanite 半透明在无 Splat 时不产生 AVBOIT 开销。
- Cook 确定性：Package Access Tracking 修复使依赖记录不再依赖加载顺序/进程。

## 🐛 Bug 修复
- Sequencer：修复撤销 Space Switch 补偿后 Spawnable 永久消失的问题；修复重合标记范围内解析单个标记的问题；Sequencer Scripting 对空输入进行防护并在指定帧求值。
- Control Rig：修复重命名控件已存在曲线时仍重映射 Sequencer 曲线的问题；修复每帧更新形状或设置时被约束控件漂移；修复 Vector/Euler Transform 值忽略 Min/Max 限制及详情面板缺少 Transform 动画通道值；修复禁用 Min/Max 限制后动画通道值不可拖动；修复复制粘贴元素丢失设置；修复 Pose Dialog 使用虚拟资产路径导致资产创建失败。
- AnimMixer：修复参数传给错误 Mixer 的问题；修复 AnimMixer 使用旧 API 的问题。
- UAF：修复 Content Browser 移动后动画内容失效；修复 Pose History 未检查缺失 Pose；修复系统输出 Pose 未写入时被错误分发；修复 FLODPose 清除标志位错误；为缓存 Pose 未写入提供警告。
- MotionWarping：修复不同轨道上重叠的 Motion Warping Notify 被忽略的问题。
- AIE：修复 Smart Compensation 旋转绕数（Euler filter）跳过 1-tick 对及在 switch-key 移动时运行的问题；Time Posing 现在将 delta 应用到 Control Rig 的 section-to-key（Anim Layers / additive / override），而非仅基础区段。
- Rendering：修复 SubstrateUintPerPixel 位组合错误；修复开启 Separate Translucency 时缩略图噪点/全黑，临时深度缓冲现在正确清除；修复 AVBOIT/MLAB 每条路径透射率应用。
- Editor：修复强制删除由多个对象编辑器编辑的资产时崩溃。
- Lumen：增加检测防止 Instance Culling Info 双重释放。
- Water：防护 Water Info LOD Gather 处理无 Quad 或退化缩放的 Landscape。
- ElectraProtron：忽略空轨道，避免影片时长被截断为零。
- RewindDebugger：修复动画姿态更新中的静态分析错误；防止 PIE 专用服务器帧混入客户端时间线；为通知轨道名称查找添加 Provider 读取作用域。
- RigVM：生成字节码调用栈包含嵌套函数名；修复旧资产子对象在 postload 时未清除 RF_Public 标志的问题。

## 🔧 API 变更
- UAF Layering：Layer Content 输入源由 `PreviousLayerOutput` 重命名为 `NestedInput`。
- UAF：Bindable Value 绑定由非反射 `TUniquePtr` 改为反射的 `TInstancedStruct` 存储。
- AssetTools：移植了 rename 前置 delegate，引擎侧支持资产重命名前回调。
- Control Rig/RigVM：补齐 Python 暴露函数，使旧版与新版资产类型的功能集一致。
- Chooser：随机化上下文结构体已暴露给 UAF。

## ⚠️ 废弃预告
- TLazyObjectPtr 弃用相关改动已重新集成，相关类型即将弃用。