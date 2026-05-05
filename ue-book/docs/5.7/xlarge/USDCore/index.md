# USD Core

> Adds support for USD SDK, UE wrapper classes and USD conversion utilities

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD资产、材质、动画等） |
| 模块 | `UnrealUSDWrapper` (Runtime), `USDClasses` (Runtime), `USDUtilities` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-16 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/USDCore) | |

## 用途

USDCore 插件为 Unreal Engine 提供了与 Pixar Universal Scene Description (USD) 生态系统集成的核心基础。它并非一个面向最终用户的工具，而是作为底层支持库存在，主要解决三个关键问题：

1.  **USD SDK 封装**：通过 `UnrealUSDWrapper` 模块，将 USD C++ SDK 的复杂 API 封装成更易于在 UE 环境中使用的形式，并处理与 UE 构建系统（如 Python3 集成）的兼容性。
2.  **UE 资产桥接**：通过 `USDClasses` 模块，定义了一套 UE 原生类（如 `UUsdAssetCache`、`UUsdPrimTwin`），用于在 UE 的对象系统中表示和管理 USD 的 Prim、Stage 等概念，实现 USD 数据与 UE 资产（如 StaticMesh、Material）之间的双向映射。
3.  **转换工具集**：通过 `USDUtilities` 模块，提供一系列静态函数和蓝图库，用于执行具体的转换操作，例如将 UE 的网格体、材质、动画序列等导出为 USD 格式，或从 USD 文件中提取数据生成 UE 资产。

简而言之，它是 UE 内所有高级 USD 功能（如 USD Stage Actor、USD 导入/导出器）的基石。

## 使用场景

-   **跨软件资产管线**：你需要在 Houdini、Maya、Blender 等支持 USD 的 DCC 软件与 Unreal Engine 之间无损交换复杂的场景、资产和动画数据。
-   **程序化内容生成**：你希望使用 USD 作为中间格式，通过脚本或程序化方式生成和组装游戏关卡或虚拟场景，然后导入到 UE 中。
-   **自定义 USD 工作流**：你需要开发自定义的 UE 编辑器工具或运行时功能，以读取、修改或生成 USD 文件，满足特定的项目管线需求。
-   **大型场景管理**：利用 USD 的分层和引用特性，在 UE 中高效管理和流式加载由多个部分组成的超大型虚拟世界。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| **UnrealUSDWrapper** | Runtime | USD C++ SDK 的底层封装，处理库链接和基础类型转换。 |
| **USDClasses** | Runtime | 定义 UE 侧表示 USD 数据的核心类（如 Stage、Prim 的代理对象）。 |
| **USDUtilities** | Runtime | 提供 UE 资产与 USD 格式之间相互转换的实用函数和蓝图库。 |

## 蓝图用法

USDCore 主要提供 C++ API，但 `USDUtilities` 模块暴露了部分蓝图功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExportToUsd` | 将 UE 资产（如 StaticMesh）导出为 USD 文件。 | `UUsdUtilsBlueprintLibrary` |
| `ImportUsdFile` | 从 USD 文件导入资产到 UE 项目。 | `UUsdUtilsBlueprintLibrary` |
| `ConvertObjectToUsd` | 将单个 UE 对象转换为 USD Prim 数据。 | `UUsdUtilsBlueprintLibrary` |

### 使用示例（蓝图描述）

在蓝图中，你可以通过 `UsdUtilsBlueprintLibrary` 的静态函数节点来调用 USD 功能。例如，要将一个 `StaticMesh` 导出为 USD：
1.  获取一个 `StaticMesh` 资产的引用。
2.  调用 `ExportToUsd` 节点，传入该网格体引用、输出文件路径和可选的导出选项。
3.  节点会返回一个布尔值表示成功与否。

## C++ 用法

### 头文件引入

```cpp
// 使用底层 USD 封装
#include "UnrealUSDWrapper.h"

// 使用 UE 侧的 USD 类
#include "UsdStage.h"
#include "UsdPrim.h"

// 使用转换工具
#include "UsdUtilsBlueprintLibrary.h"
```

### 基本用法

以下示例展示了如何通过 C++ 加载一个 USD Stage 并遍历其 Prim（概念性代码）：

```cpp
// 来源：基于 USDClasses 模块的典型用法
#include "UsdStage.h"

void LoadAndInspectUsdStage(const FString& UsdFilePath)
{
    // 1. 创建一个 UsdStage 对象来代表 USD 文件
    UE::FSdfLayer RootLayer = UnrealUSDWrapper::OpenLayer(*UsdFilePath);
    if (!RootLayer)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open USD layer: %s"), *UsdFilePath);
        return;
    }

    // 2. 从图层创建 Stage
    UsdUtils::FUsdStage UsdStage = UsdUtils::FUsdStage::Open(RootLayer);
    if (!UsdStage)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open USD stage"));
        return;
    }

    // 3. 获取根 Prim 并遍历子级
    UsdUtils::FUsdPrim RootPrim = UsdStage.GetPseudoRoot();
    for (UsdUtils::FUsdPrim ChildPrim : RootPrim.GetChildren())
    {
        UE_LOG(LogTemp, Log, TEXT("Found Prim: %s, Type: %s"),
            *ChildPrim.GetName().ToString(),
            *ChildPrim.GetTypeName().ToString());
    }
}
```

### 进阶用法

结合 `USDUtilities` 进行资产转换：

```cpp
// 来源：结合 USDUtilities 和 USDClasses 的用法
#include "UsdUtilsBlueprintLibrary.h"
#include "UsdAssetCache.h"

void ExportMeshToUsdWithCache(UStaticMesh* MeshToExport, const FString& OutputPath)
{
    // 1. 准备导出选项
    FUsdExportOptions ExportOptions;
    ExportOptions.bExportMesh = true;
    ExportOptions.bExportMaterial = true;

    // 2. 使用资产缓存来管理导出过程中生成的中间资产
    UUsdAssetCache* AssetCache = NewObject<UUsdAssetCache>();

    // 3. 调用导出工具函数
    bool bSuccess = UUsdUtilsBlueprintLibrary::ExportToUsd(
        MeshToExport,
        OutputPath,
        ExportOptions,
        AssetCache
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully exported mesh to USD: %s"), *OutputPath);
        // AssetCache 中现在包含了导出过程中引用的材质等资产的映射信息
    }
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何在模块中初始化 USD 并加载一个 Stage。

**MyUsdModule.Build.cs**
```csharp
using UnrealBuildTool;

public class MyUsdModule : ModuleRules
{
    public MyUsdModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "UnrealUSDWrapper", // 依赖底层封装
            "USDClasses"        // 依赖 UE USD 类
        });
    }
}
```

**MyUsdActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "UsdStage.h" // 来自 USDClasses 模块
#include "MyUsdActor.generated.h"

UCLASS()
class MYUSDMODULE_API AMyUsdActor : public AActor
{
    GENERATED_BODY()

public:
    AMyUsdActor();

    UPROPERTY(EditAnywhere, Category = "USD")
    FString UsdFilePath;

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "USD")
    void LoadUsdStage();

private:
    UsdUtils::FUsdStage CurrentStage;
};
```

**MyUsdActor.cpp**
```cpp
#include "MyUsdActor.h"
#include "UsdStage.h"
#include "UnrealUSDWrapper.h"

AMyUsdActor::AMyUsdActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyUsdActor::LoadUsdStage()
{
    if (UsdFilePath.IsEmpty())
    {
        UE_LOG(LogTemp, Warning, TEXT("USD File Path is empty."));
        return;
    }

    // 使用 UnrealUSDWrapper 打开图层
    UE::FSdfLayer Layer = UnrealUSDWrapper::OpenLayer(*UsdFilePath);
    if (!Layer)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open USD layer from path: %s"), *UsdFilePath);
        return;
    }

    // 使用 USDClasses 中的 FUsdStage 包装
    CurrentStage = UsdUtils::FUsdStage::Open(Layer);
    if (CurrentStage)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully loaded USD Stage from: %s"), *UsdFilePath);
        // 在这里可以对 CurrentStage 进行进一步操作
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create USD Stage object."));
    }
}
```

## 模块依赖

要使用 USDCore 插件的功能，你的模块通常需要依赖 `USDClasses` 和/或 `USDUtilities`。它们会自动传递对 `UnrealUSDWrapper` 的依赖。

| 模块 | 用途 |
|---|---|
| `Python3` | `UnrealUSDWrapper` 模块的构建依赖，用于支持 USD SDK 中的 Python 绑定。 |

## 维护状态

### 近期更新

（基于提供的创建时间 2024-05-16 推断，该插件为近期新增。）

### 维护评价

-   **年龄**：插件非常新（约1年），是 UE 5.x 版本中引入的。
-   **状态**：`.uplugin` 中 `IsBetaVersion: true`，表明该插件仍处于**实验性/Beta**阶段。这意味着其 API 和功能在未来版本中可能发生不兼容的更改。
-   **活跃度**：作为 Epic Games 官方维护的、用于关键 DCC 互操作性的插件，预计会持续更新以匹配 USD SDK 的发展和 UE 的需求。
-   **推荐**：**推荐在实验性项目或需要前沿 USD 集成的管线中使用**。对于追求稳定性的生产项目，需谨慎评估 Beta 状态带来的风险，并密切关注版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/USDCore)
- [UnrealUSDWrapper 模块文档](UnrealUSDWrapper.md)
- [USDClasses 模块文档](USDClasses.md)
- [USDUtilities 模块文档](USDUtilities.md)