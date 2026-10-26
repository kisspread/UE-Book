---
title: '2026-10-26 引擎周报'
date: '2026-10-26'
---

# 2026-10-26 引擎周报

## ✨ 新功能

- **UE Animation Framework (UAF)**：多项节点与编辑能力扩展。新增 Chooser 编辑器脚本库，并将 Chooser 表编辑暴露给 Python；Chooser 表支持 Gameplay Tag 与原生共享结构体成员绑定；新增变量监视窗口（Variable Watch Window），并支持通过控制台命令进行变量覆盖；新增 Planned Alignment Warp AnimNode；Motion Matching 节点将 EventToSearch、Availabilities、PlayRate、bKeepInteractionAlive 及 warp 属性设为可绑定；新增查询绑定到变量的通知窗口的 Blueprint 库；Align Warp notify 增加 bWarpRotation 和 bWarpTranslation 选项；函数绑定与调用函数节点支持传递参数；StateTree 节点选择器新增 `a.UAF.StateTree.HideUnsupportedNodes` CVar（默认开启）以隐藏不支持节点；Layer stack 为变量分配 Asset Instance。
- **Sequencer / Control Rig**：Control Rig Sequencer 库新增 `AddAutoBakeWithAnimSequences`，可链接并自动烘焙到预创建动画序列；Sequencer Anim Mixer 支持 Control Rig 烘焙时不弹出选项对话框；Mixer 层、节与装饰 outliner 行获得独立标识符；outliner 脚本支持锁定、静音和停用行；Sequencer 脚本 API 改进：`GetBoundObjects` 与 `GetObjectBindings` 防护空输入并在请求帧求值。
- **PoseSearch / Motion Warping**：PoseSearchInteractionAsset 调试绘制改进；`ExtractLocalSpacePose` 现支持 UAnimComposite，并避免对未处理资产返回未初始化骨骼变换。
- **Dataflow**：`TransferMeshAttributes` 合并 Main 的 inpaining 并转移默认 polygroup。

## ⚡ 性能优化

- **Sequencer**：缓存序列层级是否有未保存更改，用于保存按钮图标显示，减少重复检查。
- **nDisplay**：移除 `UDisplayClusterViewportClient::Draw` 中重复的 `UpdateLevelStreaming` 调用。
- **Control Rig**：优化多控件选中时的关键帧设置（Set Key 和 S），提高操作速度。
- **Nanite**：修复无程序化像素着色器时自定义插值器/UV 导致的冗余光栅化仓，减少开销。
- **DynamicWind**：将参数化风模式（`DynamicWind.Mode 0`）改为无状态，以适配低端硬件。

## 🐛 Bug 修复

- **Sequencer / Control Rig / Curve Editor**：
  - 修复 Alt 框选取消时保留现有关键帧选择的问题。
  - 修复聚焦子序列不再存在时 `FSequencer::Tick` 崩溃。
  - 修复 Control Rig 强制删除后 `URigVMBlueprint::GetDebugInfo` 崩溃。
  - 修复 Curve Editor 在撤销后 dummy transaction 对象被垃圾回收导致的 StoreUndo 断言。
  - Simple View 中 scrub 帧关键范围结束于该帧最后一 tick。
  - `FindOrAddBinding` 增加空 `MovieScene` 防护。
  - 修复 Anim Mixer 中由 root motion 转向的角色沿拖拽移动根骨骼的问题。
- **UAF / PoseSearch / Motion Matching**：
  - 修复 UAFACLPlugin 在 Win64 arm64 上因 `VectorRegisterCast` 与原始 ACL 寄存器导致的链接错误。
  - 修复 Montages 获取 SkeletalMeshComponent 时未使用系统输出指定组件的问题。
  - 修复 Blend Layer 节点处理缺失输入的问题。
  - 修复删除第二个带嵌入 Pose Search 数据库的资产时 `FAsyncPoseSearchDatabasesManagement::OnAssetsPreDelete` 崩溃。
  - 修复复制具有无效骨骼容器的 `FPoseSearchAssetSamplerPose` 时 check 失败。
  - 修复 ControlRig 调试绘制在 Verse 实体上偏移的问题（从 `FUAFMeshTransformComponent` 获取调试绘制变换）。
  - 修复智能补偿中移动 LookAt 约束关键帧时会错误地为子对象设置关键帧的问题。
  - 修复 mutable 中由中间 CO 未定义组件引起的 check 错误。
  - 修复 UAF 调试对象选择器在 PIE 重启后无法按名称重新连接到先前目标的问题。
  - 修复系统输出无 mesh 时不必要的 ensure（现不触发 ensure）。
  - 修复 `FUAFAnimNodeDescContainer` 保持注入修改器 desc 存活的问题。
  - 修复 Chooser 头文件错误（编译修复）。
- **其他引擎子系统**：
  - nDisplay：修复 PFM/MPCDI A3D 预览网格导出器越界读取与边缘伪影。
  - Water：修复浮力管理器销毁时悬空回调。
  - WebBrowser：修复 CEF 初始化失败后重载偶发崩溃，改善缺失/损坏 CEF DLL 的处理。
  - Dataflow：修复构造组件隐藏时节点选择崩溃。
  - BSP：防护笔刷准备与重建时缺失笔刷组件或多边形列表导致的崩溃；初始化 `UModel::RootOutside` 并跳过无模型的笔刷 actor。
  - PCG：Editor Mode 工具工作 actor 现生成在当前关卡而非 PersistentLevel。
  - Navigation：修复手动放置的 RightToLeft 点导航链接可被左到右遍历的问题。
  - NDIMedia：修复隔行输入丢失 alpha、损坏 PA16 颜色及显示高度减半的问题。
  - Slate：当 RHI 纹理无效时跳过 `FSlateTexture2DRHIRef::SetTextureData`，避免锁定空纹理。
  - Python：防护 Slate/Core tick 回调重入，避免嵌套 Slate tick（如慢任务对话框）导致重入。
  - UsdPregen：修复 Windows 上 Python override 派发无法转换结果的问题。
  - StaticMesh：修复引擎退出请求后重建静态网格时 `UStaticMesh::BeginBuildInternal` 断言失败。
  - 确保 FastGeo 在 StaticMesh 并发编译时确定性。
  - Windows：修复 `DwmExtendFrameIntoClientArea` 失败时 `FWindowsWindow::OnTransparencySupportChanged` 断言。
  - Engine：在 `UGroomComponent` 和 `ULandscapeComponent` 的 OnRegister 重新预缓存 PSO，修复运行时 cvar 切换导致的 PSOPrecache ensure。
  - Gameplay Debugger：修复 spectator 扩展（Tab）激活时 HUD 不绘制。
  - Niagara：回移植 simulation-stage undo/redo 委托生命周期修复到 5.8。
  - ASTP：修复任务工作线程释放 fence、参考姿势代理及 RefPose root lock scale 问题。
  - PoseSearch：使 UAnimComposite 上编写的通知拥有其 pose search 通知，忽略其片段的通知（行为修正）。
  - AnimationWarping：`Get Curve Value From Animation` 现从合成中读取段曲线。