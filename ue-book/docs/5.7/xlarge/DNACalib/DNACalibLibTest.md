# DNACalib Plugin v6.12.2

> DNA Calibration tool plugin

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DNACalibLib` (Runtime), `DNACalibLibTest` (Runtime), `DNACalibModule` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-10-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DNACalib) | |

## 用途

DNACalib 是一个用于校准 MetaHuman 面部动画 DNA 数据的工具插件。它提供了一套 C++ 库（`DNACalibLib`）和一个编辑器模块（`DNACalibModule`），允许开发者和艺术家通过编程方式或编辑器工具对 MetaHuman 的 DNA 文件进行精确的调整和校准。这解决了在将 MetaHuman 集成到项目中时，可能需要微调其面部动画表现以匹配特定角色或艺术风格的问题。该插件依赖于 `RigLogic` 插件，后者是 MetaHuman 面部动画系统的核心。

## 使用场景

- 你正在使用 MetaHuman 角色，但发现其默认的面部动画（如微笑、皱眉）与你的角色设定或艺术风格有细微偏差 → 使用 DNACalib 对 DNA 数据进行校准。
- 你需要批量处理多个 MetaHuman 的 DNA 文件，以统一它们的动画表现 → 使用 DNACalib 的 C++ API 编写自动化脚本。
- 你正在开发一个需要动态调整角色面部特征的系统（例如，基于游戏状态改变表情强度） → 使用 DNACalib 在运行时修改 DNA 数据。

## 蓝图用法

根据提供的模块信息，`DNACalibLib` 和 `DNACalibModule` 模块依赖于 `UnrealEd`，这表明它们可能包含编辑器工具或自定义资产类型，但其核心校准功能主要通过 C++ API 暴露。`DNACalibLibTest` 是纯测试模块，不包含蓝图 API。因此，该插件的主要使用方式是通过 C++ 代码。

## C++ 用法

### 头文件引入

```cpp
#include "DNACalibLib/DNACalibLib.h"
```

### 基本用法

以下示例展示了如何使用 DNACalib 库加载一个 DNA 文件，应用一个简单的校准命令（例如，平移一个关节），然后保存结果。此模式基于典型的校准库使用逻辑推断。

```cpp
// 假设的示例，展示核心工作流
#include "DNACalibLib/DNACalibLib.h"
#include "DNAReader.h" // 来自 RigLogic 或相关 DNA 库

void CalibrateDNAExample()
{
    // 1. 加载原始 DNA 数据
    FString OriginalDNAPath = TEXT("/Game/MetaHumans/MyCharacter.dna");
    TUniquePtr<IDNAReader> OriginalDNA = LoadDNAFromFile(OriginalDNAPath); // 需要实现或使用现有加载函数

    // 2. 创建一个校准上下文或命令列表
    // DNACalibLib 可能提供类似 FDNACalibrationContext 或命令构建器
    FDNACalibrationContext CalibrationContext;
    CalibrationContext.SetSourceDNA(MoveTemp(OriginalDNA));

    // 3. 添加校准命令
    // 例如，将名为 “jaw_joint” 的关节在 X 轴上平移 0.5 个单位
    CalibrationContext.AddCommand<FDNATranslateJointCommand>(TEXT("jaw_joint"), FVector(0.5f, 0.0f, 0.0f));

    // 4. 执行校准
    TUniquePtr<IDNAReader> CalibratedDNA = CalibrationContext.Execute();

    // 5. 保存校准后的 DNA
    FString CalibratedDNAPath = TEXT("/Game/MetaHumans/MyCharacter_Calibrated.dna");
    SaveDNAToFile(CalibratedDNAPath, CalibratedDNA.Get());
}
```

### 进阶用法

进阶用法可能涉及组合多个校准命令（平移、旋转、缩放关节，修改形态键权重等），以及处理更复杂的校准逻辑，如基于参考姿态的自动校准。

```cpp
// 组合多个命令的示例
void AdvancedCalibrationExample()
{
    // ... 加载 DNA 等步骤同上 ...

    FDNACalibrationContext Context;
    Context.SetSourceDNA(LoadDNAFromFile(TEXT("Original.dna")));

    // 组合命令：调整下巴关节并修改微笑形态键
    Context.AddCommand<FDNATranslateJointCommand>(TEXT("jaw_joint"), FVector(0.0f, 0.0f, -0.2f));
    Context.AddCommand<FDNARotateJointCommand>(TEXT("jaw_joint"), FRotator(5.0f, 0.0f, 0.0f));
    Context.AddCommand<FDNASetBlendShapeWeightCommand>(TEXT("BS_Mouth_Smile"), 0.8f); // 设置微笑权重为 80%

    // 可能还有更高级的命令，如基于另一个 DNA 文件进行匹配校准
    // Context.AddCommand<FDNAMatchToReferenceCommand>(LoadDNAFromFile(TEXT("Reference.dna")));

    TUniquePtr<IDNAReader> Result = Context.Execute();
    // ... 保存结果 ...
}
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何在一个 Actor 中使用 DNACalib 库。

**MyDNACalibActor.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDNACalibActor.generated.h"

class IDNAReader;

UCLASS()
class MYPROJECT_API AMyDNACalibActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDNACalibActor();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "DNACalib")
    void CalibrateAndApplyDNA();

private:
    // 存储原始和校准后的 DNA 数据
    TUniquePtr<IDNAReader> OriginalDNAData;
    TUniquePtr<IDNAReader> CalibratedDNAData;

    // DNA 文件路径
    UPROPERTY(EditAnywhere, Category = "DNACalib")
    FString OriginalDNAFilePath;

    UPROPERTY(EditAnywhere, Category = "DNACalib")
    FString OutputDNAFilePath;
};
```

**MyDNACalibActor.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MyDNACalibActor.h"
#include "DNACalibLib/DNACalibLib.h" // 引入 DNACalib 核心头文件
// 可能需要引入 DNA 加载/保存的工具头文件，具体取决于 DNACalibLib 的 API 设计

AMyDNACalibActor::AMyDNACalibActor()
{
    PrimaryActorTick.bCanEverTick = false;
    OriginalDNAFilePath = TEXT("/Game/DNA/Original.dna");
    OutputDNAFilePath = TEXT("/Game/DNA/Calibrated.dna");
}

void AMyDNACalibActor::BeginPlay()
{
    Super::BeginPlay();
    // 在游戏开始时加载原始 DNA
    // OriginalDNAData = LoadDNAFromFile(OriginalDNAFilePath); // 需要实现或使用库提供的函数
}

void AMyDNACalibActor::CalibrateAndApplyDNA()
{
    if (!OriginalDNAData)
    {
        UE_LOG(LogTemp, Warning, TEXT("Original DNA data not loaded!"));
        return;
    }

    // 创建校准上下文
    FDNACalibrationContext CalibrationContext;
    CalibrationContext.SetSourceDNA(OriginalDNAData->Clone()); // 使用副本进行校准

    // 添加一些示例校准命令
    // 注意：具体的命令类名和参数需要参考 DNACalibLib 的实际 API
    CalibrationContext.AddCommand<FDNATranslateJointCommand>(TEXT("eye_l_joint"), FVector(0.1f, 0.0f, 0.0f));
    CalibrationContext.AddCommand<FDNASetBlendShapeWeightCommand>(TEXT("BS_Eye_Blink"), 1.0f);

    // 执行校准
    CalibratedDNAData = CalibrationContext.Execute();

    if (CalibratedDNAData)
    {
        // 保存校准后的 DNA
        // SaveDNAToFile(OutputDNAFilePath, CalibratedDNAData.Get());
        UE_LOG(LogTemp, Log, TEXT("DNA calibration completed and saved to %s"), *OutputDNAFilePath);

        // 在这里，你可能需要将校准后的 DNA 应用到 MetaHuman 组件上
        // 例如，通过 UMetaHumanComponent 或相关接口重新加载 DNA
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("DNA calibration failed!"));
    }
}
```

## 模块依赖

要使用 DNACalib 插件，你的项目模块需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `DNACalibLib` | 核心校准算法库，提供所有校准命令和上下文。 |
| `RigLogic` | MetaHuman 面部动画驱动库，DNACalib 依赖其定义的 DNA 数据结构和读写接口。 |
| `UnrealEd` | `DNACalibLib` 和 `DNACalibModule` 依赖此模块，表明它们可能包含编辑器工具、自定义资产类型或需要在编辑器环境下运行的功能。 |

**注意**：`DNACalibLibTest` 是测试模块，仅用于开发验证，不应在你的项目模块中依赖。

## 维护状态

### 近期更新

```
- 9e83f7eeef40 [DNACalibLibTest] * Changed so test module does not add DNACalibLib code if building with merged modules since we know they end up in the same dll
- 914f2d844019 Move DNACalib under public plugins folder and add DNACalib2 under restricted folder #rb violeta.vukobrat
```
*   第一条提交优化了测试模块的构建逻辑，避免在合并模块时重复添加代码。
*   第二条提交将 DNACalib 插件移动到了公开插件目录，并提到了一个受限的 DNACalib2 插件，表明该功能正在持续开发和组织。

### 维护评价

DNACalib 是一个相对较新的插件（创建于 2024 年 10 月），并且有近期的代码提交记录，表明它处于**活跃维护**状态。作为 Epic Games 官方维护的 MetaHuman 工具链的一部分，其稳定性和支持是有保障的。该插件是 MetaHuman 工作流中的重要一环，推荐在需要对 MetaHuman 面部动画进行深度定制的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DNACalib)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DNACalib/Source/DNACalibLibTest) (位于 `DNACalibLibTest` 模块内)