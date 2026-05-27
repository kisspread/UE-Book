# GPU Lightmass

> Static lighting building & previewing system using DXR

| 属性 | 值 |
|---|---|
| 中文名 | GPU 光照贴图 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GPULightmass` (UncookedOnly), `GPULightmassEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GPULightmass) | |

## 用途

GPU Lightmass 是 UE5 中基于 DXR（DirectX 光线追踪）的**实时/交互式光照贴图烘焙系统**，用于替代传统 CPU 端的 Lightmass。

传统 Lightmass 通过 CPU 进行光线追踪计算，场景越大、分辨率越高，烘焙时间越长（可能数小时）。GPU Lightmass 利用显卡的硬件光线追踪单元（需要支持 DXR 的 GPU）进行路径追踪，大幅提升烘焙速度，同时支持**交互式预览**——移动摄像机时能实时看到光照效果。

核心能力：
- **路径追踪全局光照**（GI）：通过多跳路径追踪计算间接光照
- **辐照度缓存**（Irradiance Caching）：对室内场景优化 GI 强度准确性
- **首次反弹光线引导**（First Bounce Ray Guiding）：针对窗户等主要光源方向优化采样
- **固定光阴影**（Stationary Light Shadows）：分离计算并存储
- **体积光照贴图**（Volumetric Lightmap）：3D 体素化采样
- **降噪**：支持 Intel OIDN 和简易萤火虫滤除两种方案
- **虚拟纹理预览**：通过虚拟纹理系统实现渐进式渲染预览
- **两种烘焙模式**：Full Bake（完整烘焙）和 Bake What You See（所见即所烤）

⚠️ **仅支持 Win64 + SM5 + DXR 硬件**。

## 使用场景

- 你有一个室内/室外场景，需要快速迭代光照效果 → 用 GPU Lightmass 的交互式预览
- 你的美术团队需要频繁调整灯光参数并即时看到结果 → 使用 "Bake What You See" 模式
- 你需要比传统 Lightmass 更快的烘焙速度 → GPU 并行路径追踪
- 你的场景包含大量静态光照的固定光（Stationary Light）→ GPU Lightmass 支持单独的阴影通道计算
- 你需要体素级的体积光照贴图来照亮粒子/动态物体 → 体积光照贴图功能

## 蓝图用法

GPU Lightmass 通过 `UGPULightmassSubsystem`（世界子系统）暴露控制接口，以及 `UGPULightmassSettings` 暴露所有烘焙参数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Launch` | 启动光照贴图烘焙 | `UGPULightmassSubsystem` |
| `Stop` | 停止正在运行的烘焙 | `UGPULightmassSubsystem` |
| `IsRunning` | 查询烘焙是否正在运行 | `UGPULightmassSubsystem` |
| `GetPercentage` | 获取当前烘焙进度百分比（0-100） | `UGPULightmassSubsystem` |
| `GetSettings` | 获取当前世界的 GPU Lightmass 设置对象 | `UGPULightmassSubsystem` |
| `SetRealtime` | 设置是否以实时模式运行（影响烘焙速度） | `UGPULightmassSubsystem` |
| `Save` | 保存当前烘焙结果 | `UGPULightmassSubsystem` |
| `StartRecordingVisibleTiles` | 开始录制可见的虚拟纹理瓦片 | `UGPULightmassSubsystem` |
| `EndRecordingVisibleTiles` | 结束录制可见瓦片 | `UGPULightmassSubsystem` |

### 设置参数（UGPULightmassSettings）

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Mode` | `EGPULightmassMode` | FullBake | FullBake（全场景）或 BakeWhatYouSee（仅可视区域） |
| `GISamples` | int | 512 | 每纹素的 GI 采样数（32-65536） |
| `StationaryLightShadowSamples` | int | 128 | 固定光阴影采样数 |
| `bUseIrradianceCaching` | bool | true | 是否启用辐照度缓存（室内场景推荐开启） |
| `bUseFirstBounceRayGuiding` | bool | false | 首次反弹光线引导（室内+窗户场景推荐） |
| `DenoisingOptions` | enum | OnCompletion | 降噪时机：None/OnCompletion/DuringInteractivePreview |
| `Denoiser` | enum | IntelOIDN | 降噪器：IntelOIDN 或 SimpleFireflyRemover |
| `bCompressLightmaps` | bool | true | 是否压缩光照贴图纹理（关闭可减少伪影但增加 4x 内存） |
| `VolumetricLightmapDetailCellSize` | int | 200 | 体积光照贴图最密体素的世界单位大小 |
| `LightmapTilePoolSize` | int | 55 | GPU 瓦片池大小（影响 GPU 内存） |
| `bShowProgressBars` | bool | true | 是否在瓦片内显示绿色进度条 |
| `TilePassesInSlowMode` | int | 1 | 实时查看器模式的速度倍率 |
| `TilePassesInFullSpeedMode` | int | 8 | 非实时模式的速度倍率 |

### 使用示例（蓝图描述）

**启动烘焙：**
1. 从世界上下文获取 `UGPULightmassSubsystem` 子系统
2. 调用 `GetSettings` 获取设置对象
3. 根据需要修改 `GISamples`、`Mode` 等参数
4. 调用 `Launch` 开始烘焙

**监控进度：**
1. 每帧调用 `GetPercentage` 获取进度
2. 调用 `IsRunning` 检查是否完成
3. 监听子系统的 `OnLightBuildEnded` 委托

**Bake What You See 流程：**
1. 设置 `Mode` 为 `BakeWhatYouSee`
2. 调用 `Launch`
3. 移动摄像机查看不同区域
4. 完成后调用 `Save` 保存结果

## C++ 用法

GPU Lightmass 主要通过世界子系统 API 和编辑器集成使用。以下示例展示如何通过 C++ 控制烘焙流程。

### 头文件引入

```cpp
#include "GPULightmassSettings.h"
#include "GPULightmassModule.h"
```

### 基本用法

```cpp
// 从 FGPULightmassModule 获取当前世界的静态光照系统
// 来源: Public/GPULightmassModule.h

#include "GPULightmassModule.h"

// 获取模块实例
FGPULightmassModule& GPULightmassModule = FModuleManager::GetModuleChecked<FGPULightmassModule>("GPULightmass");

// 检查系统是否正在运行
bool bRunning = GPULightmassModule.IsStaticLightingSystemRunning();
```

### 通过子系统控制烘焙

```cpp
// 来源: Public/GPULightmassSettings.h - UGPULightmassSubsystem

UGPULightmassSubsystem* Subsystem = World->GetSubsystem<UGPULightmassSubsystem>();

// 获取并配置设置
UGPULightmassSettings* Settings = Subsystem->GetSettings();
Settings->Mode = EGPULightmassMode::BakeWhatYouSee;
Settings->GISamples = 1024;
Settings->DenoisingOptions = EGPULightmassDenoisingOptions::OnCompletion;

// 启动烘焙
Subsystem->Launch();

// 监听完成事件
Subsystem->OnLightBuildEnded().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("GPU Lightmass bake completed!"));
});
```

### 进阶用法

```cpp
// 录制可见瓦片以用于 Bake What You See 模式
// 来源: Private/GPULightmass.h

UGPULightmassSubsystem* Subsystem = World->GetSubsystem<UGPULightmassSubsystem>();

// 开始录制可见瓦片
Subsystem->StartRecordingVisibleTiles();

// ... 移动摄像机浏览场景 ...

// 停止录制
Subsystem->EndRecordingVisibleTiles();

// 切换实时模式影响烘焙速度
Subsystem->SetRealtime(true);  // 慢速，不阻塞编辑器
Subsystem->SetRealtime(false); // 全速烘焙

// 保存结果
Subsystem->Save();
```

## 模块依赖

GPU Lightmass 的核心独特依赖是光线追踪渲染和虚拟纹理系统：

| 模块 | 用途 |
|---|---|
| `RenderRayTracing` | DXR 硬件光线追踪支持 |
| `VirtualTexturing` | 虚拟纹理系统，用于渐进式光照贴图预览 |
| `IntelOIDN` | Intel Open Image Denoise 降噪库（可选） |
| `RenderCore` | RDG 渲染依赖图、Shader 编译 |
| `MeshDescription` | 网格数据处理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `78d4e656` | [GPULM] Flush deferred SBT static-range frees on cached scene teardown | 修复缓存场景销毁时 SBT 静态范围延迟释放的刷新问题 |
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership | HWRT 重构：统一网格批次所有权管理 |
| 2026-04-21 | `a437915f` | [HWRT] Refactored shared vertex buffer management in FRayTracingDynamicGeometryUpdateManager | HWRT 重构动态几何体顶点缓冲区管理 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 统一 GPU 同步 API，替换旧调用 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 迁移日志宏到 UE_LOGF 格式 |

### 维护评价

GPU Lightmass 自 2020 年创建以来**持续活跃维护**，近几个月仍有多次实质性更新（2026 年 4-5 月），主要集中在：
- 光线追踪底层架构优化（SBT 管理、动态几何体缓冲区）
- API 现代化（UE_LOG 迁移、GPU 同步调用统一）
- Bug 修复

该插件仍标记为 **Beta + Experimental**，`EnabledByDefault=false`，需要手动启用。虽然核心功能已经相当完善，但 Epic 尚未将其提升为正式功能，表明可能仍有已知的限制或稳定性问题。

**推荐使用**：如果你的项目需要快速迭代静态光照且有 DXR 兼容 GPU，GPU Lightmass 是一个优秀的选择。但需注意：
- 仅支持 Win64 平台
- 需要支持 DXR 的 GPU（RTX 2060+ 或同等）
- 仍在 Beta 阶段，某些场景可能出现渲染伪影
- 不建议用于最终发布版本的光照烘焙，除非经过充分验证

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GPULightmass)
- 官方文档：无
- [设置类源码](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/GPULightmass/Source/GPULightmass/Public/GPULightmassSettings.h)