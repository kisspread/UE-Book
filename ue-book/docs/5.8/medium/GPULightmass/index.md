# GPU Lightmass

> Static lighting building & previewing system using DXR

| 属性 | 值 |
|---|---|
| 中文名 | GPU 光照构建 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `GPULightmass` (UncookedOnly), `GPULightmassEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GPULightmass) | |

## 用途

GPU Lightmass 是一个利用 DirectX Raytracing (DXR) 技术在编辑器中**实时构建和预览静态光照**的插件。它旨在替代或补充传统的基于 CPU 的 Lightmass 系统，为场景设计师和光照美术提供**极快的迭代速度**。其核心价值在于，允许用户在调整灯光、材质等属性后，在**数秒或分钟内**看到近似最终质量的光照效果，而无需等待漫长的 CPU 构建过程，极大地提高了工作流效率。

## 使用场景

- 你正在为一个**室内或室外环境**调整光照布局，需要快速预览不同灯光设置下的效果。
- 你正在测试不同的**材质和光照交互**，希望实时看到全局光照（GI）的变化。
- 你在进行**光照烘焙的快速原型验证**，在投入长时间的 CPU 构建前进行快速检查。
- 你使用**支持硬件光追的显卡**（如 NVIDIA RTX 系列），并希望充分利用其性能进行光照构建。

## 蓝图用法

插件主要通过编辑器菜单和工具栏进行交互，底层蓝图接口较少。核心操作通过子模块提供的工具类和编辑器扩展完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartBuild` | 启动一次 GPU 光照构建过程 | `UGPULightmassSubsystem` |
| `StopBuild` | 停止当前的构建过程 | `UGPULightmassSubsystem` |
| `GetBuildState` | 查询当前的构建状态（就绪、构建中等） | `UGPULightmassSubsystem` |
| `GetProgress` | 获取当前构建的进度（0.0 - 1.0） | `UGPULightmassSubsystem` |

### 使用示例（蓝图描述）

通常在编辑器工具栏或“构建光照”菜单中直接点击“GPU Lightmass Build”按钮启动。在蓝图中，你可以通过 `Get GameInstance Subsystem` 节点获取 `GPULightmassSubsystem`，然后调用上述函数来编程控制构建流程。

## C++ 用法

主要在编辑器工具和子系统层面进行扩展和控制。

### 头文件引入

```cpp
#include "GPULightmassSubsystem.h"
```

### 基本用法

```cpp
// 获取世界中的GPU Lightmass子系统并启动构建
UWorld* World = GEditor->GetEditorWorldContext().World();
if (UGPULightmassSubsystem* GPULightmassSubsystem = World->GetSubsystem<UGPULightmassSubsystem>())
{
    // 配置构建参数（如果需要）
    // FGPUStaticLightingSettings Settings;
    // GPULightmassSubsystem->SetSettings(Settings);
    
    // 启动构建
    GPULightmassSubsystem->StartBuild();
}
```

### 进阶用法

```cpp
// 监听构建完成事件（委托绑定）
// 假设你有一个类MyEditorTool，它需要在构建完成后执行一些操作
// void UMyEditorTool::OnBuildFinished(bool bSuccess)
// {
//     if (bSuccess) { /* 更新预览或保存光照 */ }
// }
// 
// // 绑定委托
// if (UGPULightmassSubsystem* Subsystem = World->GetSubsystem<UGPULightmassSubsystem>())
// {
//     Subsystem->OnBuildCompleted.AddDynamic(this, &UMyEditorTool::OnBuildFinished);
// }
```

## Demo 示例

**最小可运行示例（在编辑器工具类中）**：
```cpp
// MyLightmassTestTool.h
#pragma once
#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "MyLightmassTestTool.generated.h"

UCLASS()
class UMyLightmassTestTool : public UObject
{
    GENERATED_BODY()

public:
    /** 启动GPU光照构建 */
    UFUNCTION(BlueprintCallable, Category = "Lightmass Test")
    static void RunGPULightmassBuild();
};

// MyLightmassTestTool.cpp
#include "MyLightmassTestTool.h"
#include "GPULightmassSubsystem.h"
#include "Editor.h"

void UMyLightmassTestTool::RunGPULightmassBuild()
{
    if (!GEditor) return;
    UWorld* EditorWorld = GEditor->GetEditorWorldContext().World();
    if (!EditorWorld) return;

    UGPULightmassSubsystem* Subsystem = EditorWorld->GetSubsystem<UGPULightmassSubsystem>();
    if (Subsystem)
    {
        UE_LOG(LogTemp, Log, TEXT("Starting GPU Lightmass build..."));
        Subsystem->StartBuild();
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("GPULightmassSubsystem not found. Is the plugin enabled?"));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RenderCore` | 底层渲染核心功能，用于命令提交和资源管理。 |
| `RHI` | 渲染硬件接口，用于访问 DXR (DirectX Raytracing) 相关功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `78d4e656` | [GPULM] Flush deferred SBT static-range frees on cached scene teardown | 优化了缓存场景销毁时的着色器绑定表 (SBT) 内存管理。 |
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership. | 统一了硬件光追中动态几何体更新的网格批处理所有权模型。 |
| 2026-04-21 | `a437915f` | [HWRT] Refactored shared vertex buffer management in FRayTracingDynamicGeometryUpdateManager. | 重构了硬件光追动态几何体管理器中的共享顶点缓冲区管理。 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 重构了 GPU 命令提交与等待机制，简化了 API。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏统一迁移为更现代的格式。 |

### 维护评价

GPU Lightmass 插件虽然标记为实验性且默认禁用，但从 git 历史来看，**维护非常活跃**。最近的提交（2026年）集中在**底层渲染性能优化、内存管理改进和 API 统一**上，这些都是实质性的技术优化，表明 Epic 仍在持续开发和打磨此功能。尽管创建已约 6 年，但其技术迭代从未停止。由于它依赖于 DXR，因此存在**平台和硬件限制**（仅支持 Win64，需要支持 DXR 的显卡）。对于追求快速光照迭代且硬件条件允许的项目，**强烈推荐尝试使用**，尤其是在 UE5 的 Lumen 系统之外需要更高精度静态光照的场景。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GPULightmass)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/GPULightmass/Tests/)