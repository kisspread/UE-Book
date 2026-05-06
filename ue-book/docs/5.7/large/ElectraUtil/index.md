# Electra Player Utilities

> Reusable Base Components for Electra Player Media Playback

| 属性 | 值 |
|---|---|
| 中文名 | Electra 工具集 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraBase` (Runtime), `ElectraHTTPStream` (Runtime), `ElectraSamples` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-24 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraUtil) | |

## 总体用途

ElectraUtil 是 **Electra 媒体播放器** 的基础组件库。它将播放器底层跨平台基础设施、HTTP 流传输层以及音视频样本缓冲区管理抽象为独立模块，供上层播放器实现（如 `ElectraPlayer` 插件）或自定义媒体管道使用。

- **解决什么问题**：避免在每个媒体播放器实现中重复编写平台抽象、网络传输和缓冲区池化代码，提供开箱即用且性能优化的基础库。
- **为什么存在**：Electra 媒体框架需要一套统一、可重用的运行时组件来支持多平台（Win64 / Mac / iOS / Android / Linux）的媒体播放，同时允许用户进行定制（如自定义 HTTP 请求头、Buffer 处理策略）。

## 模块列表

| 模块 | 一句话总结 | 详细文档 |
|---|---|---|
| `ElectraBase` | 跨平台基础类型、实用工具类（字符串、时间、日志、容器等），所有 Electra 相关组件的通用依赖。 | [ElectraBase.md](./ElectraBase.md) |
| `ElectraHTTPStream` | 可定制的异步 HTTP/HTTPS 流传输层，支持请求/响应管理、进度回调、多路传输。 | [ElectraHTTPStream.md](./ElectraHTTPStream.md) |
| `ElectraSamples` | 音视频样本缓冲区管理，提供基于 CPU 和 GPU（D3D11/D3D12）的样本池，支持同步与资源回收。 | [ElectraSamples.md](./ElectraSamples.md) |

## 使用场景

- **构建自定义媒体播放器**：当需要基于 Electra 框架开发自有播放器时，直接依赖此插件获取跨平台基础工具和 HTTP 传输能力。
- **流媒体应用**：需要从 HTTP(S) 源加载媒体数据，并希望对该层进行精细控制（如自定义证书验证、代理设置）。
- **视频渲染优化**：利用 `ElectraSamples` 提供的 GPU 缓冲区池，避免每帧频繁分配/释放显存，适合高性能渲染管线。
- **跨平台移植**：插件已屏蔽平台差异（例如 DirectX 版本选择、文件路径处理），降低多平台适配成本。

## 维护状态

### 近期更新（最近 5 次 commit）

```
- 2025-09-25 e6018661 ElectraUtils: Fixed check to BufferAvailable() in the DX12 buffer helpers
- 2025-09-25 83ef846c ElectraSamples: Fixed Linux server build linker error
- 2025-09-25 916bb820 ElectraSamples: calling ShutdownPoolable() in the destructor to avoid potential resource leaks
- 2025-09-24 241a7987 ElectraUtil: Removing hard limit of number of buffer slots in favor of dynamic resizes
- 2025-09-24 7d7c63bd ElectraUtil: fixed DX12 GPU buffer helper heap issues
```

### 维护评价

- 该插件于 **2025-09-24** 首次创建，属于全新插件。
- 创建后两天内连续提交了 5 次实质性更新，包括功能优化（动态缓冲区扩容）、平台修复（Linux server 链接错误）、资源泄漏修复等，说明 **维护非常活跃**。
- 尚未发现已知重大问题或废弃标记，可以放心使用。
- 注意：插件默认 **未启用**（`EnabledByDefault=false`），需要在项目设置中手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraUtil)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)（Electra Media 框架总览）
- [模块文档: ElectraBase](./ElectraBase.md)
- [模块文档: ElectraHTTPStream](./ElectraHTTPStream.md)
- [模块文档: ElectraSamples](./ElectraSamples.md)