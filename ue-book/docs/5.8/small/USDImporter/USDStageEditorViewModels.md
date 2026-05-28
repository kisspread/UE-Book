# USD Stage Editor View Models

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD阶段编辑器视图模型 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `USDStageEditorViewModels` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

`USDStageEditorViewModels` 是 `USDImporter` 插件中 **USD Stage 编辑器** 的**数据模型与视图模型**模块。它并不直接处理 USD 文件的导入导出，而是为编辑器中预览、浏览和交互式编辑 USD Stage 的 UI（如属性面板、层级树、图层管理）提供核心的数据结构与业务逻辑。它将复杂的 USD 概念（如 Prim、Layer、Variant、Reference）封装成易于 Slate UI 框架使用的 ViewModel，是构建 USD 可视化编辑工作流的基础。

## 使用场景

- 你正在为 Unreal Engine 开发一个自定义的 USD 资产浏览器或查看器，需要高效地展示 USD Stage 的树状层级结构（Prim 树）。
- 你需要实现一个类似 `USDStageEditor` 的面板，允许用户查看和编辑某个 USD Prim 的元数据、属性、关系，并管理其 Payload 和 Variant 选择。
- 你想要构建一个 USD 图层（Layer）管理界面，让用户可以切换编辑目标、静音图层或添加子图层。
- 你需要一个数据模型来驱动一个显示 USD Prim 引用（References）和 Payload 列表的界面。

## 蓝图用法

本模块主要为 C++ 和 Slate UI 服务，**不包含直接的蓝图可调用节点**。其 ViewModel 类是纯数据结构和逻辑封装，供其他模块（如 `USDStageEditor`）的 Slate Widget 或 Actor 组件使用。蓝图用法主要通过 `AUsdStageActor` 及其提供的函数间接实现（参见 `USDStage` 模块文档）。

## C++ 用法

### 头文件引入

```cpp
#include "USDPrimViewModel.h"
#include "USDLayersViewModel.h"
#include "USDStageViewModel.h"
// 根据需要引入其他 ViewModel 头文件
```

### 基本用法：构建一个 Prim 树的 ViewModel

以下代码演示如何创建一个 `FUsdStageViewModel` 并加载一个 Stage，然后遍历其根 Prim 来填充树视图模型。

**来源参考**: `USDStageEditorViewModels` 模块的公共接口设计，以及 `USDTests` 模块中的类似用法模式。

```cpp
#include "USDStageViewModel.h"
#include "USDPrimViewModel.h"
#include "UsdStage/UsdStage.h"

void BuildPrimTreeViewModel()
{
    // 1. 创建 Stage 视图模型
    FUsdStageViewModel StageViewModel;

    // 假设我们有一个 AUsdStageActor (通常在编辑器中由工具或用户操作创建)
    AUsdStageActor* StageActor = /* 获取或创建的 Stage Actor */;
    StageViewModel.UsdStageActor = StageActor;

    // 2. 打开一个 USD 文件
    const TCHAR* FilePath = TEXT("/Game/USD/my_asset.usda");
    StageViewModel.OpenStage(FilePath);

    // 3. 获取 Stage 引用 (通过 Actor 间接获取)
    UE::FUsdStageWeak UsdStage = StageActor->GetUsdStage();

    if (UsdStage.IsValid())
    {
        // 4. 创建根 Prim 的 ViewModel
        // UsdStage->GetPseudoRoot() 获取 Stage 的根节点
        auto RootPrimViewModel = MakeShared<FUsdPrimViewModel>(nullptr, UsdStage, UsdStage->GetPseudoRoot());

        // 5. 填充其子节点 (递归地构建树)
        RootPrimViewModel->FillChildren();

        // 现在 RootPrimViewModel->Children 包含了第一层子 Prim 的 ViewModel 列表
        // 可以将 RootPrimViewModel 传递给自定义的 Slate TreeView 控件进行显示
    }
}
```

### 进阶用法：响应和修改 Prim 的属性

以下示例展示了如何使用 `FUsdObjectFieldsViewModel` 来读取和设置 Prim 的属性值。

**来源参考**: `USDStageEditor` 模块中属性面板的实现逻辑。

```cpp
#include "USDObjectFieldViewModel.h"
#include "USDPrimViewModel.h"
#include "UsdUtils.h"

void EditPrimAttribute(const UE::FUsdStageWeak& UsdStage, const UE::FUsdPrim& UsdPrim)
{
    if (!UsdStage.IsValid() || !UsdPrim.IsValid())
    {
        return;
    }

    // 1. 创建属性字段的 ViewModel
    FUsdObjectFieldsViewModel FieldsViewModel;

    // 2. 刷新数据，指定要查询的 Prim 路径和时间码
    FString PrimPath = UsdPrim.GetPath().GetString();
    FieldsViewModel.Refresh(UsdStage, *PrimPath, UsdStage->GetTimeCode());

    // 3. 查找名为 “MyAttribute” 的属性并修改其值
    for (const auto& Field : FieldsViewModel.Fields)
    {
        if (Field->Label == TEXT("MyAttribute") && Field->Type == EObjectFieldType::Attribute)
        {
            // 假设我们已知它是一个浮点数属性
            UsdUtils::FConvertedVtValue NewValue;
            NewValue.BasicType = UsdUtils::EUsdBasicDataTypes::Float;
            NewValue.Value = (float)3.14f;

            Field->SetAttributeValue(NewValue);
            break;
        }
    }
}
```

## Demo 示例

这是一个完整的、可编译的最小示例，展示了如何创建一个 `AUsdStageActor`，并使用其相关 ViewModel 加载一个 Stage 并打印根 Prim 的名称。

**MyUsdStageActor.h**
```cpp
// MyUsdStageActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyUsdStageActor.generated.h"

UCLASS()
class MYPROJECT_API AMyUsdStageActor : public AActor
{
    GENERATED_BODY()

public:
    AMyUsdStageActor();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "USD")
    void LoadUsdStage(const FString& FilePath);

    // 用于存储实际的 USD Stage Actor (由引擎管理)
    UPROPERTY()
    AUsdStageActor* InternalUsdStageActor;
};
```

**MyUsdStageActor.cpp**
```cpp
// MyUsdStageActor.cpp
#include "MyUsdStageActor.h"
#include "USDStageActor.h"
#include "USDStageViewModel.h"
#include "USDPrimViewModel.h"
#include "UsdStage/UsdStage.h"

AMyUsdStageActor::AMyUsdStageActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyUsdStageActor::BeginPlay()
{
    Super::BeginPlay();

    // 在游戏开始时自动加载一个示例文件
    LoadUsdStage(TEXT("/Game/USD/sample.usda"));
}

void AMyUsdStageActor::LoadUsdStage(const FString& FilePath)
{
    // 创建或查找场景中的 AUsdStageActor
    if (!InternalUsdStageActor)
    {
        InternalUsdStageActor = GetWorld()->SpawnActor<AUsdStageActor>();
    }

    if (InternalUsdStageActor)
    {
        // 使用 StageViewModel 来执行操作 (封装了 Actor 的逻辑)
        FUsdStageViewModel StageViewModel;
        StageViewModel.UsdStageActor = InternalUsdStageActor;

        StageViewModel.OpenStage(*FilePath);

        // 现在可以获取 Stage 并创建 ViewModel 进行进一步操作
        UE::FUsdStageWeak UsdStage = InternalUsdStageActor->GetUsdStage();
        if (UsdStage.IsValid())
        {
            auto RootViewModel = MakeShared<FUsdPrimViewModel>(nullptr, UsdStage, UsdStage->GetPseudoRoot());
            UE_LOG(LogTemp, Log, TEXT("USD Stage loaded. Root Prim: %s"), *RootViewModel->GetName().ToString());

            // 可以将此 RootViewModel 存储起来，用于驱动 UI
        }
    }
}
```

**使用方式**:
1.  将 `MyUsdStageActor` 放入关卡。
2.  在 `BeginPlay` 中它会自动尝试加载 `sample.usda` 文件。
3.  你也可以在运行时通过蓝图调用 `LoadUsdStage` 函数来加载其他文件。
4.  加载成功后，会在日志中打印根 Prim 的名称。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `USDSchemas` | 提供 USD Schema 的基础类型和功能，是 ViewModel 理解 USD 数据结构的基石。 |
| `USDClasses` | 包含核心的 USD 类型封装（如 `FUsdStage`, `FUsdPrim`, `FSdfLayer`），是 ViewModel 操作 USD 数据的主要接口。 |
| `USDStage` | 提供 `AUsdStageActor` 的核心功能，StageViewModel 与之紧密交互。 |
| `USDClassesEditor` | 提供编辑器特定的 USD 工具函数和类型。 |

*(注意：`Core`, `CoreUObject`, `Engine`, `Slate`, `UMG` 等常见依赖已省略)*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量转换为 float 时产生的编译警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD：支持绑定不依赖蓝图的控制绑定。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va | USD：解决26.03版本更新导致的LOD变化时AnimQuery内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正32位格式说明符在参数为64位时应使用64位，反之亦然。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD：烘焙曝光动画轨道的所有帧。 |

### 维护评价

- **创建时间**：该插件于2018年底创建，历史悠久。
- **维护状态**：**活跃维护中**。从提供的近期提交记录（截至2026年）可以看出，该模块连同整个 `USDImporter` 插件仍在被 Epic Games 持续更新，修复兼容性问题、适配新版 USD 库（如26.03）并添加新功能（如控制绑定支持）。
- **已知问题**：`.uplugin` 中标记为 `IsBetaVersion: true` 和 `EnabledByDefault: false`，表明该功能仍被视为实验性，可能存在未稳定的 API 或功能边界。使用者需注意其可能带来的风险。
- **推荐使用**：**是的，但需谨慎**。对于需要在 Unreal Engine 中深度使用 USD 进行资产交换、协作或构建自定义工具链的高级项目，尤其是影视和建筑可视化领域，该插件及其视图模型模块是目前 Epic 官方提供的最佳（也是唯一）深度集成方案。由于其“实验性”状态和底层依赖的复杂性，建议在版本控制下使用，并做好应对 API 变更的准备。

## 相关链接

- [源码 (USDImporter 根目录)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档]() (暂无)
- [测试用例 (USDTests 模块)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)