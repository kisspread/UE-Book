# D3D12 Video Decoders Electra

> Uses GPU vendor provided accelerators under Direct3D 12 Video（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | D3D12硬件视频解码 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `D3D12VideoDecodersElectra` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-19 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/D3D12VideoDecodersElectra) | |

## 用途

该插件为 Unreal Engine 的 Electra 媒体播放器提供基于 Direct3D 12 Video API 的硬件加速视频解码能力。它利用 GPU 厂商（NVIDIA、AMD、Intel 等）提供的硬件解码器，在 Windows 平台上实现 H.264 和 H.265（HEVC）视频的 GPU 端解码，从而大幅降低 CPU 占用，提升高清/4K 视频的播放性能。

该插件解决的核心问题是：在 Windows 平台上，当 Electra 媒体播放器需要播放 H.264/H.265 编码的视频时，可以将解码工作从 CPU 卸载到 GPU 的专用硬件单元（如 NVIDIA NVDEC、AMD VCN 等），实现高效的硬件加速解码。

插件内部通过 D3D12 Video Device API 枚举设备支持的解码格式和 Profile，管理解码后的图片缓冲区（DPB），并通过 D3D12 Fence 对象实现 CPU-GPU 同步。

## 使用场景

- 你在 Windows 平台上使用 Electra 媒体播放器播放 H.264/H.265 视频，需要降低 CPU 占用 → 启用此插件
- 你正在开发一个需要播放大量高清视频内容的应用（如虚拟制片、实时视频合成）→ 启用此插件以获得硬件解码性能
- 你希望在项目中使用 Electra 播放器并自动利用 D3D12 硬件解码 → 需要手动启用此插件（默认未启用）

## 蓝图用法

此插件**没有暴露任何蓝图 API**。所有解码器类均为内部实现，不包含 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。解码器由 Electra 媒体播放器框架在内部自动选择和调用。

启用此插件后，当你通过 Electra 播放器加载支持的视频格式时，系统会自动检测并使用 D3D12 硬件解码路径。

## C++ 用法

此插件的所有类均位于 `Private` 目录下，不对外暴露公共 C++ API。它作为 Electra 编解码器系统的一个内部实现模块，通过 ElectraCodecs 的解码器工厂机制自动注册和选择。

开发者无需直接调用本插件的任何类，只需启用插件即可让 Electra 自动利用 D3D12 硬件解码。

### 支持的编解码器

从源码中提取的支持格式：

| 编解码器 | 8-bit | 10-bit |
|---|---|---|
| H.264 | ✅ | ❌ |
| H.265 (HEVC) | ✅ | ✅ |
| VP9 | GUID 已定义 | GUID 已定义 |

> **注意**：VP9 的 Profile GUID 已在 `FCodecFormatHelper` 中定义，但未发现对应的解码器实现类（仅有 `FD3D12VideoDecoder_H264` 和 `FD3D12VideoDecoder_H265`）。AV1、VP8 的 GUID 被注释掉，暂不支持。

### 平台限制

- **仅限 Win64** 平台
- **排除 Server** 目标（`TargetDenyList: ["Server"]`）

## Demo 示例

由于此插件不暴露公共 API，无需编写自定义代码。以下是使用此插件的完整流程：

### 使用步骤

1. **启用插件**：在项目的 `.uproject` 文件中添加：
```json
{
    "Plugins": [
        {
            "Name": "D3D12VideoDecodersElectra",
            "Enabled": true
        }
    ]
}
```

2. **使用 Electra 播放器播放视频**：通过 Media Framework 或 Media Texture 正常播放 H.264/H.265 视频，系统会自动选择 D3D12 硬件解码路径。

### 内部架构概览（供参考）

```
ElectraCodecs (解码器框架)
  └─ FD3D12VideoDecoder (基类 - D3D12 通用逻辑)
       ├─ FD3D12VideoDecoder_H264 (H.264 实现)
       └─ FD3D12VideoDecoder_H265 (H.265 实现)
```

关键内部类：
- `FCodecFormatHelper` — 查询 GPU 支持的编解码格式和 Profile
- `FDecodedPictureBuffer` — 管理解码后的帧缓冲区（DPB）
- `FSyncObject` — 基于 D3D12 Fence 的 CPU-GPU 同步对象
- `FVideoDecoderOutputD3D12Electra` — 解码输出，实现 `IElectraDecoderVideoOutput` 接口

## 模块依赖

### 插件依赖

| 插件 | 用途 |
|---|---|
| `ElectraCodecs` | Electra 编解码器框架，提供解码器基类接口和工厂注册机制 |

### 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。插件通过 Build.cs 引入 D3D12/DXGI/DXVA/MediaFoundation 等 Windows 平台头文件，但这些属于平台 SDK 依赖，无需在使用者的模块中额外声明。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-20 | `3ed2062b` | ElectraDecoders: modernized the decoder factory to be more usable for other clients | 现代化解码器工厂，提升对其他客户端的可用性 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移：从 UE_LOG 迁移到 UE_LOGF |
| 2026-03-10 | `56829cdc` | Electra: D3D12 HEVC video decoding related changes | D3D12 HEVC 视频解码相关改动 |
| 2025-11-19 | `514ccff4` | ElectraCodecs: Add information about the decoder implementation being used for decoding. | 添加解码器实现信息，便于调试识别当前使用的解码器 |
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 代码规范化：将析构函数改为 = default |

### 维护评价

**活跃维护** — 该插件创建于 2024 年 2 月，至今约 2 年，属于较新的插件。最近一次更新（2026-04-20）距今仅约 5 天，更新频率稳定。近半年内有功能性更新（HEVC 解码改动、解码器工厂现代化），且包含代码质量改进（日志宏迁移、析构函数规范化）。作为 Electra 媒体播放器硬件解码管线的重要组成部分，该插件仍在积极维护中。

**注意事项**：
- 该插件默认未启用（`EnabledByDefault: false`），需要手动启用
- 仅支持 Windows 平台的 D3D12 后端
- VP9 支持处于定义阶段，尚无完整实现

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/D3D12VideoDecodersElectra)
- 官方文档（无）
- [ElectraCodecs 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayerPlugin/Source/ElectraCodecs)（父依赖插件）