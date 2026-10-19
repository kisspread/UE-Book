---
title: '2026-10-19 引擎周报'
date: '2026-10-19'
---

# 2026-10-19 引擎周报

## ✨ 新功能

- UAF：图 Action Menu 搜索现在会匹配节点 Keywords 元数据；Motion Matching 节点 UX 改进；Bindable object picker 支持 RequiredAssetDataTags。
- UAF：AnimGenController 新增 notify 支持；AnimDatabase 新增 FindAttribute。
- UAF：新增对 AnimOp 输出 NaN 和非规范化旋转的校验；ApplyAdditiveSpace 支持 weight 大于 1.0 时外推 bound/unbound 值；AnimNode 强制子条目在动画树图中声明的 base。
- Sequencer：粘贴 Sections 到 blendable track 时，重叠区域现在会被替换，而不是堆叠隐藏副本。
- PoseSearch：新增 FAsyncPoseSearchDatabasesManagement::OnAsyncBuildIndexCompleted 回调，项目代码可获知数据库索引完成。
- Sony SDK：新增对 SDK 14 的支持，最高版本仍默认为 SDK 13。
- HWRT：支持 Nanite assembly parts 作为 append instances 实例化到 TLAS；append instances 超预算时新增日志和屏显警告。
- ASTP Anim Sequence Transform Provider：新增 mirroring、root motion、stateless track playback 支持，并修复 exact bounds 与 lifecycle 问题。
- Nanite Ray Tracing：为 BLASClusterCountBuffer 添加 EBufferUsageFlags::SourceCopy。

## 🚀 重大变更

- HWRT：移除 5.8 已废弃的代码；移除未使用的 bApplyLocalBoundsTransform 路径。

## ⚡ 性能优化

- UAF：移除 blend AnimOps 中冗余的 normalize 调用；Layering 从缓存 pose 读取 layer input，减少重复计算。
- RigLogic：反序列化后释放未使用的内存，降低内存占用。
- Nanite Ray Tracing：用 per-part capacity vector 取代原先基于 GetNumBLAS 与 NumResidentClusters 的 CLAS 地址预留，改由 hierarchy traversal 实际输出的 cluster 数量通过 readback 提供。
- HWRT：更新更多 GetDynamicRayTracingInstances 实现以使用 GPUScene，避免手动提交 InstanceTransforms。
- DynamicWind：改善剔除诊断，并减少 shader permutations。
- TEDS Compat：immediate mode 下批量移除 UObject rows，按批次触发 observers 并 flush commands。

## 🐛 Bug 修复

- UAF：修复 TUAFCoWRef 自赋值问题；修复 bindable value resolution 多个 bug；修复 TPool 反向迭代；修复 blend two ops 忽略 immutable empty inputs；修复清除 timed transition source 导致 source 仍 parent 到 blend out modifier；修复 AnimTree 日志缺少文件名。
- PoseSearch：修复 UPoseSearchDatabase::GetNormalizedAssetTime 中 null Database 解引用崩溃；修复 mesh skeleton 与 animation skeleton 不匹配时 UpdateConstraints 崩溃；修复 FSearchResults 移动构造函数相关问题；修复 OnObjectPropertyChanged 上 FPoseSearchColumn 的线程安全 ensure。
- Sequencer：修复撤销后重新验证关键帧选择崩溃；修复恢复无对象绑定的 Control Rig pre-animated state 崩溃；修复 TDynamicSparseBitSet 跨首个 bucket 的查找和合并错误；修复 scheduled entity task 无 required components 时 ForcePrePostTask 未被遵守。
- Control Rig：修复 auto-compile off 下编辑变量后 SetExternalVariablesInstanceData 断言；修复加载时 patch functions 崩溃及复制粘贴函数重复 Guid；修复 Control Rig edit mode 退出后 Anim Outliner 刷新崩溃；修复 AIE 中 Control Rig Timewarp Baking。
- HairStrands：修复 groom binding 重置或销毁仍在渲染时 FHairStrandsLODRestRootResource::GetBulkData 的渲染线程断言；修复整体设置 physics/interpolation 数组时 groom interpolation 断言。
- Nanite：修复 WPO 在运行时启用时 Max World Position Offset Displacement 不生效的问题；修复关闭编辑器时 Nanite assembly build 等待依赖导致 FStaticMeshCompilingManager 断言。
- Nanite Ray Tracing / HWRT：修复 NaniteRayTracingGeometryClusterCutTraversalCS 未考虑 assembly LOD error scale；修复缺失 Nanite assembly part BLAS；修复 view indices 复用时 raytracing scene stats readback bug；修复 Nanite::FSceneProxy 中 RayTracingProxy 为 null 导致的崩溃；修复 FMeshRenderBufferSet 未设置 IndexBufferStride；修复 ray tracing feedback 若干问题。
- MediaIOCore：修复捕获从未创建资源的帧时崩溃。
- 平台与打包：MacOS 15 上 cp -R 到符号链接失败，改用 rsync -a；电影文件始终作为 NonUFS 处理，避免使用原生 OS/media API 的 streamer 无法播放；移除 WinGDK remote device IDs 后缀以修复 Turnkey。
- PCG：修复 World Partition 地图中 PCG editor mode tools 生成 actor 未创建 external package；修复子系统过早查询的 tentative 问题。
- Landscape：修复 target layer 名称不匹配时未解除 layer info 分配。
- StaticMesh / UnrealEd：修复 StaticMesh RenderData 初始化；为 vertex-snapping 迭代器增加缺失 mesh data 的 guard。
- Movie Render Pipeline：修复 pipeline 同步关闭且正在 flush engine systems 时可能发生的崩溃。
- Mesh Partition：修复 shared pipe implementation 中 MT access detector 的竞态条件。
- DeformerGraph：在 UOptimusNodeGraph 中拒绝 null 输入，避免崩溃或添加坏节点。
- Online Services Xbl：始终实现模块，避免未启用 GDK 时项目无法使用。
- nDisplay：在游戏线程释放 FSceneViewStateReference，并向 GC 报告 view-state UObjects。
- MetaHuman：跳过 bulk payload 小于 TextureInfo 时的高清纹理 Source.Init；拒绝重入 TryAddObjectToEdit；修复关闭编辑器时 HostedAssetEditorToolkit.IsValid 断言；修复 wardrobe 使用无效纹理缩略图崩溃；guard InvisibleDrivingActor。
- DaySequence：从 easing pickers 中隐藏 UDaySequenceModifierEasingFunction，并 guard 未绑定的 Evaluate。
- Shader：修复异步 shader 编译禁用时崩溃和编译卡住。
- Mutable：修复 Laplacian Smoothing 时潜在的 buffer overrun。
- 网络：Backport ServerMutePlayer null TSharedRef 解引用修复。

## 🔧 API 变更

- UAF：Chooser 剩余参数转换为 UAF Bindables；Sanitize value transformer 与 AnimOp 重命名为 Normalize。
- HWRT：NativeInstances 重命名为 TLASInstances；移除 RayTracingInstanceBufferUtil.h 的 UE_INTERNAL；将标记为 ERayTracingInstanceFlags::NaniteRayTracing 的实例处理移至 Nanite::FRayTracingManager。

## ⚠️ 废弃预告

- DDC：非废弃 DDC 图不再使用 Local cache store，统一改用 ZenLocal；同时废弃过渡期提供的 fallback graphs。