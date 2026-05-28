# GPU Lightmass

> Static lighting building & previewing system using DXR

| 属性 | 值 |
|---|---|
| 中文名 | GPU光照烘焙 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板） |
| 模块 | `GPULightmass` (UncookedOnly), `GPULightmassEditor` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GPULightmass) | |

## 用途
GPULightmass 是一个使用 DXR（DirectX Raytracing）技术替代传统 CPU 光照烘焙的系统。它旨在通过 GPU 加速实现更快的光照贴图构建和交互式光照预览，从而大幅缩短游戏开发中的关卡光照迭代时间。该插件解决了传统 CPU 光照烘焙（Lightmass）速度慢、反馈延迟的痛点，特别适合需要频繁调整静态光照的场景。

## 使用场景
- 你正在开发一个大型开放世界游戏，需要烘焙大量光照贴图，并希望在编辑器中快速看到光照修改效果。
- 你是一名关卡设计师或灯光师，正在反复调试场景的静态光照，希望获得接近实时的反馈。
- 你的项目使用 Lumen 进行动态全局光照，但仍需要高质量的静态光照贴图作为补充或回退方案。

## 蓝图用法
蓝图 API 主要通过 `FGPULightmassSubsystem` 提供。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `GPULightmass_PreviewLighting` | 启动/更新当前视口的交互式光照预览 | `FGPULightmassSubsystem` |
| `GPULightmass_BuildLighting` | 构建选中Actor或整个场景的静态光照数据 | `FGPULightmassSubsystem` |
| `GPULightmass_Cancel` | 取消正在进行的预览或构建任务 | `FGPULightmassSubsystem` |

### 使用示例（蓝图描述）
在编辑器工具蓝图中，你可以：
1. 从事件图表中拖出 `Get GPULightmass Subsystem` 节点，获取子系统实例。
2. 连接 `GPULightmass_PreviewLighting` 节点以触发实时预览。
3. 使用 `GPULightmass_BuildLighting` 节点并传入一组Actor引用，构建特定对象的光照。
4. 通过轮询或事件绑定 `IsBuilding` 属性来监控构建状态。

## C++ 用法

### 头文件引入
```cpp
#include "GPULightmassSubsystem.h"
```

### 基本用法
获取子系统并调用预览功能。
*（来源：Editor 主动测试场景）*
```cpp
// 获取编辑器子系统
if (UGPULightmassSubsystem* GPULightmassSubsystem = GEditor->GetEditorSubsystem<UGPULightmassSubsystem>())
{
    // 开始交互式光照预览
    GPULightmassSubsystem->PreviewLighting();
    
    // 构建选中物体的光照
    TArray<AActor*> SelectedActors;
    // ... 获取选中的Actor ...
    GPULightmassSubsystem->BuildLighting(SelectedActors);
}
```

### 进阶用法
处理异步操作和获取结果。
*（来源：构建流程测试）*
```cpp
UGPULightmassSubsystem* Subsystem = GEditor->GetEditorSubsystem<UGPULightmassSubsystem>();

// 绑定构建完成委托
Subsystem->OnBuildComplete.AddLambda([](bool bSuccess)
{
    if (bSuccess)
    {
        UE_LOG(LogGPULightmass, Log, TEXT("GPU Lightmass build completed successfully."));
    }
});

// 启动构建，不阻塞编辑器
Subsystem->BuildLighting(/* Params */);

// 或者，等待构建完成
Subsystem->WaitForBuildCompletion();

// 获取烘焙好的光照贴图资产
UTexture* Lightmap = Subsystem->GetBakedLightmapTextureForActor(MyActor);
```

## Demo 示例

### 最小 C++ 示例：在编辑器按钮点击后触发构建
```cpp
// MyEditorTool.h
#pragma once
#include "EditorUtilityWidget.h"
#include "MyEditorTool.generated.h"

UCLASS()
class UMyEditorTool : public UEditorUtilityWidget
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable)
    void OnBuildLightingButtonClicked();
};

// MyEditorTool.cpp
#include "MyEditorTool.h"
#include "GPULightmassSubsystem.h"

void UMyEditorTool::OnBuildLightingButtonClicked()
{
    if (UGPULightmassSubsystem* Subsystem = GEditor->GetEditorSubsystem<UGPULightmassSubsystem>())
    {
        // 对所有静态网格体Actor执行GPU光照构建
        Subsystem->BuildLightingForAllStaticMeshActors();
    }
}
```

## 模块依赖
| 模块 | 用途 |
|---|---|
| `D3D12RHI` | 底层DX12渲染硬件接口，用于执行DXR光线追踪命令 |
| `RenderCore`, `RHI` | 核心渲染与硬件抽象层 |
| `RayTracing` | 光线追踪核心库，提供场景加速结构与着色器支持 |
| `MeshDescription`, `StaticMeshDescription` | 处理静态网格体数据以构建加速结构 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `78d4e656` | [GPULM] Flush deferred SBT static-range frees on cached scene teardown | 优化缓存场景清理时SBT内存释放 |
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership. | 统一光追动态几何体的网格批次管理 |
| 2026-04-21 | `a437915f` | [HWRT] Refactored shared vertex buffer management in FRayTracingDynamicGeometryUpdateManager. | 重构光追动态几何体的顶点缓冲区管理 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 统一GPU同步等待函数 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏 |

### 维护评价
- **创建时间**：2020年，已超过5年。
- **维护状态**：**活跃维护中**。截至2026年5月仍有频繁的提交，内容涉及性能优化、光追核心功能重构和Bug修复。
- **平台限制**：仅支持 **Win64** 平台。
- **已知限制**：标记为 **实验性 (Beta)**，且 **默认未启用**。稳定性与功能完整性可能不及正式特性。
- **推荐度**：**有条件推荐**。对于使用 DXR 兼容显卡（如 NVIDIA RTX 系列）且开发环境为 Win64 的团队，如果你的项目对光照烘焙速度有极高要求，愿意承担实验性功能的风险，可以尝试使用。它能显著提升迭代效率，但需注意其潜在的限制和平台依赖性。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GPULightmass)