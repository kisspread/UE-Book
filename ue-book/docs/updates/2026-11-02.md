---
title: '2026-11-02 引擎周报'
date: '2026-11-02'
---

# 2026-11-02 引擎周报

## ✨ 新功能

- **LumenWorldCache**：引入自动表面缓存，取代依赖预计算 mesh cards 的 LumenSurfaceCache。新系统采用完全随机光照，为 Lumen 提供更通用的全局光照缓存。
- **LumenPT**：从 LumenRef 重命名为 LumenPT，作为实验性直接与间接光照参考模式，并新增高度雾支持。
- **Nanite Ray Tracing**：新增 FNaniteRayTracingSceneExtension 和 FNaniteRayTracingSceneExtensionRenderer 的基础支持，为 Nanite 硬件光线追踪场景管理提供扩展框架。
- **HWRT**：有限支持 Nanite ISM/HISM 的 world position offset，统一了静态网格、ISM、HISM 和 Nanite proxy 的 ray tracing world position offset 策略，并添加 DecodeRayTracingInstanceId 以正确路由 GPUScene 实例查找。

## 🚀 重大变更

- **移除实验性 Lumen 路径**：移除 r.LumenScene.DirectLighting.Stochastic 1 随机表面缓存光照路径和 r.LumenScene.GPUDrivenUpdate GPU 驱动更新路径，由新的 LumenWorldCache 取代。
- **HWRT 数据迁移**：将 ray tracing 数据迁移至 FRayTracingSceneExtension，移除 FPrimitiveSceneInfo 等中的废弃代码，并统一 ray tracing world position offset 策略。
- **MegaLights**：移除 Global SDF tracing 支持。

## ⚡ 性能优化

- **Lumen 系列**：World Cache accumulation buffer 不再每帧清空，仅清理修改条目，但需额外 16MB 非瞬态内存；屏幕像素 dispatch 改为 8x4 tile 波形处理；Lumen scene lighting 与 trace paths 多项 GPU 优化；radiance cache HWRT 减少 pass 依赖并跳过不必要的合成 pass，在 console 上节省约 0.06ms；直接与间接光照分开 dispatch 以重叠异步队列执行。
- **HWRT**：使用 bitmask 替代 set 跟踪 referenced geometry groups，重构 cached ray tracing data 的失效与更新逻辑，修复竞争条件，并为 SBT 与异步 compute 上 raygen shader pass 添加同步。
- **RDG**：新增 AddBarrierPass UAV 变体以支持 SkipBarrier 标志的 UAV，避免不必要的 barrier；修复 FRDGBuilder::AddPassDependency 数据竞争和 ExcludeList 未正确处理的问题。
- **AssetRegistry**：gather cache 分片根据 tag data 大小而非仅 asset count 进行划分。

## 🐛 Bug 修复

- **StylusInput**：修复 RealTimeStylus COM 对象泄漏及释放顺序问题，修复 Wintab 光标按钮名多于实际按钮数时的崩溃。
- **HWRT**：修复特定场景下 ray tracing scene 缺失 primitives、instanced static meshes 和 Nanite proxies 相关问题，修复平台预览禁用 raytracing 时的错误，修复 CLAS 装配部件 hit shader 中 WorldNormal 不正确的问题。
- **Ray Tracing**：翻转几何法线以匹配 detail normal，修复双面材质上的多种渲染 bug。
- **MegaLights**：修复体积效果忽略 IES 配置文件的问题，修复不支持 async compute 平台上的崩溃。
- **Lumen**：在 mesh card 捕获期间禁用全局距离场，修复 raster 与 Lumen Surface Cache 使用距离场采样节点时的结果不一致；使用随机浮点量化修复 R11G11B10_Float 存储 World Cache lighting 时的颜色漂移；修复 World Cache 禁用时的路径提前终止并替换为 Russian roulette。
- **UAF**：修复 BindableValueCustomization；FUAFMirrorAnimOp 在骨架层级变化时重建缓存；FRemapPoseData 检测参考姿势骨骼网格变化；notify injection 仅允许通过 FUAFNotifyInjectedModifierDesc 显式 opt-in 的 modifier。
- **ChaosVehicles**：修复 vehicle manager 销毁时对 stale vehicles 的 assert。
- **UMG**：推迟 UCheckBox 和 UWidgetSwitcher 中 FieldNotify 广播，直到 Slate widget 更新。
- **World Light Grid**：收紧 CVar 钳位，防止误设过高 r.Forward.WorldLightGrid.Resolution 时因内存不足而崩溃。

## 🔧 API 变更

- 移除 FPrimitiveSceneInfo::AddStaticMeshes 和 FPrimitiveSceneInfo::UpdateStaticMeshes 中未使用的参数。
- 新增 GRHIGlobals.RayTracing.SupportsAsyncRayTraceDispatchIndirect 全局变量，用于检查平台是否支持异步 compute 上的间接 raygen dispatch。
- 支持在 FD3D12CommandContext 上覆盖 DispatchRays 行为。
- RDG 新增 AddBarrierPass UAV 变体。
- HWRT 数据迁移至 FRayTracingSceneExtension，相关 API 结构发生变化。