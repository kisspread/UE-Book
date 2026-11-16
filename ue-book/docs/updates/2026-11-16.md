---
title: '2026-11-16 引擎周报'
date: '2026-11-16'
---

# 2026-11-16 引擎周报

## ✨ 新功能

- StateTree 现已支持 transition payloads，可在状态转换之间传递数据，并相应调整了 transition payload 相关的 static_asserts。
- HWRT/RHI 新增 RHICopyAccelerationStructures，可将已构建的 BLAS 克隆到另一个具有等价拓扑的 geometry 中，之后可基于该 geometry 自身的 vertex buffers 进行更新。
- Static Meshes 对 OMM（Opacity Micromap）的支持已落地第一阶段，并提供了基础 opacity micromap ray tracing 测试与 shared micromap curve helpers。
- LumenWorldCache 新增 clipmap 控制参数：r.Lumen.WorldCache.FirstClipmapRadius 和 r.Lumen.WorldCache.ClipmapResolution。
- Web 错误卡上的“发送报告”按钮现在会说明报告发送的内容和去向。

## 🚀 重大变更

- HWRT 的 BLAS compaction 现在由 FRayTracingGeometryManager 显式执行，默认开启（r.RayTracing.Compaction.Explicit=1）；如需回退到旧的 RHI 内部 compaction，可在启动时将该值设为 0。同时移除了 RHI 侧的 BLAS compaction request handlers。
- HWRT/RHI 不再在 RHI 层维护 ray tracing geometry streaming 概念。FRayTracingGeometry 的 streaming 状态改为统一的 NotStreamable / StreamedOut / StreamedIn 枚举，并通过 SetInitializer 设置。

## ⚡ 性能优化

- FAnimNode_SaveCachedPose 优化：当缓存的 pose 不会被复用时，不再执行缓存。
- HWRT/RHI 仅在实际能够读取 ray tracing hit group parameters 时才进行设置，避免无用参数设置开销。
- LumenWorldCache 在 mod 256 cell coordinate keys 回绕前主动 evict 条目，避免因 key 回绕导致缓存定位错误。

## 🐛 Bug 修复

- WebGPU RHI 多项修复：render pass 内记录的 CPU buffer upload 不再错误切分 pass；非 4 字节对齐的 CPU buffer write 会保留相邻字节；pipeline 因 internal 或 out-of-memory 错误创建失败后不会继续保持绑定；GPU frame time 会忽略不推进的 begin-of-pass timestamp；主线程 WebGPU 调用抛出 JavaScript exception 时通过错误卡停止游戏；prewarm 记录的 pipeline 可在 canvas format 不同的 device 上正确匹配。
- Web/Wasm 平台修复：IO-worker size 请求对瞬时 HTTP 错误进行重试，失败时不再将 size 误报为 0 字节；UBT 在 no-op Wasm 构建中保留 makefile，确保新添加文件在下次构建可被发现；查询 mask 在长串无 `=` 的 `?` 下改为线性时间处理；fatal stop 后游戏不再在错误卡背后继续运行；修复 Staging 日志占位符与参数数量不匹配的问题；crash report 仅发送固定字段列表并记录 CrashGUID，构建机写入带 line records 的 crash symbols。
- Web shader format 现在会转换 memory-only barriers，而不是直接 stub 掉整个 shader。
- nDisplay：从 camera view 获取 DoF focal length，保证 tiled 和 overscanned inner frustums 保留相机的深度场效果。
- Mac WebBrowser：正确处理 WKWebView 下载，避免将下载内容当作导航加载。
- Pose Driver：修复当前 LOD 剥离 source bone 时发生的崩溃。
- CommonUI：修复关闭 modal 后焦点恢复到已禁用 widget 的问题；KeepSharedInputModeTags 现在按 local player 统计 active activatable widgets 添加或移除的 input mode tags，共享 tag 会保留到最后一个持有它的 widget 取消激活。
- FAnimNode_SaveCachedPose：防止循环 cached pose link 导致的重入 Update/Evaluate。
- TmvMedia Transcoder：修复 transcode 在取消、超时或失败时仍有帧在编码导致的崩溃。
- UMG：修复 ToggleWidgetAsVariable 会修改属于其他 Widget Blueprint 的 widget 的问题。
- RDG：修复多个 AddSetupTask overload 未透传 WaitPoint 的问题。
- HWRT：修复 ray tracing 禁用期间创建的 skeletal mesh static geometry streaming 状态，并在 LOD stream-in 时跳过已 evicted 的 geometry。
- UAF：为 RunScriptEventByName 添加 UE_MT_SCOPED_WRITE_ACCESS guard。

## 🔧 API 变更

- HWRT/RHI：FRayTracingGeometry 的 streaming state 改为统一枚举（NotStreamable / StreamedOut / StreamedIn），并通过 SetInitializer 设置；新增 FRayTracingCompactedSizeCS 全局 shader，用于需要 compute pass 写入 BLAS compacted sizes 的平台；向高层代码开放 BLAS compaction 功能。
- StateTree：新增 transition payload 支持，相关 static_asserts 由 TIsDerivedFrom 替换为新的检查方式。