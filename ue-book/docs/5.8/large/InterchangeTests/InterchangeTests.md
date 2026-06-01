# Interchange Tests

> Plugin for Interchange automation tests.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 交换测试框架 |
| 分类 | Testing |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeTestEditor` (Runtime), `InterchangeTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-02-20 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/InterchangeTests) | |

## 用途

这是一个 **Interchange 资产导入/导出系统的自动化测试框架**，而非面向终端用户的功能插件。它存在的目的是为 Epic 内部及开发者提供一套可扩展的测试基础设施，用于验证 Interchange 框架在各种资产类型（静态网格、骨骼网格、材质、纹理、动画、灯光、关卡序列等）的导入和重新导入流程中是否正确工作。

该框架支持：
- **测试计划定义**：通过 JSON 文件或编辑器内资产定义导入测试场景，包含源文件、管线设置、验证步骤
- **导入与重新导入测试**：支持完整的导入→验证→重新导入→再验证工作流
- **截图对比**：自动截取视口画面并与基准图进行像素级比较，用于视觉回归测试
- **丰富的断言库**：针对每种资产类型提供数十个专用验证函数（顶点数、三角形数、LOD 数、材质槽、骨骼权重等）
- **管线设置覆盖**：测试中可自定义 Interchange Pipeline 参数，验证不同管线配置的导入行为

简单来说：**如果你正在开发或维护 Interchange 导入/导出功能，或者正在编写自定义 Pipeline，这个插件就是你做回归测试的基础设施。**

## 使用场景

- 你在开发新的 Interchange Import Pipeline → 用此框架编写测试计划，确保你的改动不会破坏已有功能
- 你需要验证某个 3D 格式（如 FBX/glTF）导入后资产属性是否正确 → 配置测试计划并运行自动化检查
- 你在做 Interchange 的 bug fix → 编写测试复现问题，修复后运行测试确认不会回归
- 你需要对导入结果做视觉对比 → 利用截图测试功能捕获视口并与基准图比较
- 你在为团队制定资产导入规范 → 使用测试计划作为可执行的验收标准

## 蓝图用法

本插件主要面向编辑器内测试计划编辑和自动化执行，蓝图可访问的 API 较为精简。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetPipelinePropertiesAsJSON` | 将 Pipeline 对象的属性序列化为 JSON 字符串 | `UInterchangeTestsBlueprintFunctionLibrary` |
| `RunThisTest` | 在编辑器中立即运行当前测试计划（CallInEditor） | `UInterchangeImportTestPlan` |

### 使用示例（蓝图描述）

**在编辑器中运行测试计划：**

1. 在 Content Browser 中右键 → 创建 `InterchangeImportTestPlan` 资产
2. 打开资产编辑器，填写 `Description`（测试描述）
3. 在 `Import` 分类下配置 `ImportStep`：
   - 设置 `SourceFile`（相对于 JSON 脚本的源文件路径）
   - 如需自定义管线，勾选 `bUseOverridePipelineStack` 并添加 Pipeline
4. 在 `Reimport` 分类下添加重新导入步骤（可选）
5. 点击 `RunThisTest` 按钮立即执行，或通过自动化测试面板批量运行

**截图对比测试配置：**

在 `ImportStep` 或 `ReimportStep` 中：
1. 勾选 `bTakeScreenshot`
2. 配置 `ScreenshotParameters`：
   - `bAutoFocus`：自动聚焦到指定 Actor
   - `CameraLocation` / `CameraRotation`：手动设置摄像机位置
   - `ComparisonTolerance`：设置像素对比容差（Low/Medium/High）
   - `ViewMode`：设置视口模式（Lit/Wireframe 等）

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeImportTestPlan.h"
#include "InterchangeImportTestStepBase.h"
#include "InterchangeTestFunction.h"
#include "ImportTestFunctions/StaticMeshImportTestFunctions.h"
```

### 基本用法：创建自定义资产测试函数

通过继承 `UImportTestFunctionsBase` 并使用 `UFUNCTION(Exec)` 标记测试函数来扩展测试框架。

**来源**: `Public/ImportTestFunctions/ImportTestFunctionsBase.h`

```cpp
// 基于框架的约定，创建自定义资产类型的测试函数类
UCLASS(MinimalAPI)
class UMyAssetImportTestFunctions : public UImportTestFunctionsBase
{
    GENERATED_BODY()

public:
    // 必须重写此方法，指定该测试函数集关联的资产类型
    virtual UClass* GetAssociatedAssetType() const override
    {
        return UMyAsset::StaticClass();
    }

    // 测试函数必须标记为 UFUNCTION(Exec)
    // 框架通过反射机制获取默认参数值，而非通过控制台调用
    UFUNCTION(Exec)
    static FInterchangeTestFunctionResult CheckMyAssetProperty(
        UMyAsset* Asset, int32 ExpectedValue)
    {
        FInterchangeTestFunctionResult Result;
        if (Asset->GetValue() != ExpectedValue)
        {
            Result.AddError(FString::Printf(
                TEXT("Expected value %d, got %d"),
                ExpectedValue, Asset->GetValue()));
        }
        return Result;
    }
};
```

### 基本用法：理解测试函数结果结构

**来源**: `Public/InterchangeTestFunction.h`

```cpp
// FInterchangeTestFunctionResult 用于收集测试结果
FInterchangeTestFunctionResult Result;

// 添加信息级别日志
Result.AddInfo(TEXT("检查开始"));

// 添加警告（不导致测试失败）
Result.AddWarning(TEXT("某些值接近阈值"));

// 添加错误（导致测试失败）
Result.AddError(TEXT("顶点数不匹配"));

// 检查是否通过
if (Result.IsSuccess())
{
    // 测试通过，无错误
}
```

### 进阶用法：通过反射系统调用测试函数

**来源**: `Public/InterchangeTestFunction.h`

```cpp
// FInterchangeTestFunction 是测试计划中的核心结构
// 它通过反射机制动态绑定测试函数和参数

// 获取指定资产类型可用的测试函数列表
TArray<UFunction*> Functions = FInterchangeTestFunction::GetAvailableFunctions(
    UStaticMesh::StaticClass());

// 获取可用的资产类型列表
TArray<UClass*> AssetClasses = FInterchangeTestFunction::GetAvailableAssetClasses();

// 创建并配置一个测试函数调用
FInterchangeTestFunction TestFunction;
TestFunction.AssetClass = UStaticMesh::StaticClass();
TestFunction.OptionalAssetName = TEXT("MyMesh");
TestFunction.CheckFunction = Find<UFunction>(TEXT("CheckLodCount"));
TestFunction.Parameters.Add(FName(TEXT("ExpectedNumberOfLods")), TEXT("3"));

// 导入参数（从文本转为二进制）
TSharedPtr<FStructOnScope> ParamData = TestFunction.ImportParameters();

// 调用测试函数
TArray<UObject*> AssetsToTest;
AssetsToTest.Add(MyStaticMesh);
FInterchangeTestFunctionResult Result = TestFunction.Invoke(AssetsToTest);
```

### 进阶用法：使用静态网格验证函数

**来源**: `Public/ImportTestFunctions/StaticMeshImportTestFunctions.h`

```cpp
// UStaticMeshImportTestFunctions 提供了丰富的网格验证 API
// 所有函数均为 static，直接调用即可

// 检查导入的静态网格数量
auto R1 = UStaticMeshImportTestFunctions::CheckImportedStaticMeshCount(
    MeshArray, 1);  // 期望导入 1 个静态网格

// 检查 LOD 数量
auto R2 = UStaticMeshImportTestFunctions::CheckLodCount(
    Mesh, 3);  // 期望 3 个 LOD

// 检查顶点数
auto R3 = UStaticMeshImportTestFunctions::CheckVertexCount(
    Mesh, 0, 1024);  // LOD 0 期望 1024 个顶点

// 检查材质槽数量
auto R4 = UStaticMeshImportTestFunctions::CheckMaterialSlotCount(
    Mesh, 2);  // 期望 2 个材质槽

// 与基准资产进行对比（支持多种对比维度）
auto R5 = UStaticMeshImportTestFunctions::CheckAgainstGroundTruth(
    Mesh, GroundTruthMesh,
    true,   // bCheckVertexCountEqual
    true,   // bCheckTriangleCountEqual
    true,   // bCheckUVChannelCountEqual
    true,   // bCheckCollisionPrimitiveCountEqual
    true,   // bCheckVertexPositionsEqual
    true);  // bCheckNormalsEqual

// 检查 Nanite 设置
FMeshNaniteSettings NaniteSettings;
NaniteSettings.bEnabled = true;
auto R6 = UStaticMeshImportTestFunctions::CheckNaniteSettings(
    Mesh, NaniteSettings);
```

### 进阶用法：骨骼网格验证

**来源**: `Public/ImportTestFunctions/SkeletalMeshImportTestFunctions.h`

```cpp
// 检查骨骼数量
auto R1 = USkeletalMeshImportTestFunctions::CheckBoneCount(
    SkeletalMesh, 56);

// 检查 Morph Target
auto R2 = USkeletalMeshImportTestFunctions::CheckMorphTargetCount(
    SkeletalMesh, 3);
auto R3 = USkeletalMeshImportTestFunctions::CheckMorphTargetName(
    SkeletalMesh, 0, TEXT("Smile"));

// 检查指定骨骼的蒙皮顶点数
auto R4 = USkeletalMeshImportTestFunctions::CheckSkinnedVertexCountForBone(
    SkeletalMesh, TEXT("head"), false, 256);
```

## Demo 示例

以下示例展示如何在 C++ 中创建一个自定义测试函数类来验证自定义资产类型的导入结果。

### MyAssetTestFunctions.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "ImportTestFunctions/ImportTestFunctionsBase.h"
#include "InterchangeTestFunction.h"
#include "MyAssetTestFunctions.generated.h"

class UMyCustomAsset;

/**
 * 为自定义资产类型提供 Interchange 导入测试函数
 */
UCLASS(MinimalAPI)
class UMyAssetTestFunctions : public UImportTestFunctionsBase
{
    GENERATED_BODY()

public:
    /** 返回此测试函数集关联的资产类型 */
    virtual UClass* GetAssociatedAssetType() const override;

    /** 检查导入的自定义资产数量是否符合预期 */
    UFUNCTION(Exec)
    static FInterchangeTestFunctionResult CheckImportedAssetCount(
        const TArray<UMyCustomAsset*>& Assets,
        int32 ExpectedCount);

    /** 检查资产的关键属性值 */
    UFUNCTION(Exec)
    static FInterchangeTestFunctionResult CheckAssetName(
        UMyCustomAsset* Asset,
        const FString& ExpectedName);

    /** 检查资产的数值属性范围 */
    UFUNCTION(Exec)
    static FInterchangeTestFunctionResult CheckValueInRange(
        UMyCustomAsset* Asset,
        float MinValue,
        float MaxValue);
};
```

### MyAssetTestFunctions.cpp

```cpp
#include "MyAssetTestFunctions.h"
#include "MyCustomAsset.h"

UClass* UMyAssetTestFunctions::GetAssociatedAssetType() const
{
    return UMyCustomAsset::StaticClass();
}

FInterchangeTestFunctionResult UMyAssetTestFunctions::CheckImportedAssetCount(
    const TArray<UMyCustomAsset*>& Assets,
    int32 ExpectedCount)
{
    FInterchangeTestFunctionResult Result;

    if (Assets.Num() != ExpectedCount)
    {
        Result.AddError(FString::Printf(
            TEXT("Expected %d imported assets, but got %d"),
            ExpectedCount, Assets.Num()));
    }
    else
    {
        Result.AddInfo(FString::Printf(
            TEXT("Imported asset count matches: %d"), ExpectedCount));
    }

    return Result;
}

FInterchangeTestFunctionResult UMyAssetTestFunctions::CheckAssetName(
    UMyCustomAsset* Asset,
    const FString& ExpectedName)
{
    FInterchangeTestFunctionResult Result;

    if (!Asset)
    {
        Result.AddError(TEXT("Asset is null"));
        return Result;
    }

    if (Asset->GetName() != ExpectedName)
    {
        Result.AddError(FString::Printf(
            TEXT("Expected asset name '%s', but got '%s'"),
            *ExpectedName, *Asset->GetName()));
    }

    return Result;
}

FInterchangeTestFunctionResult UMyAssetTestFunctions::CheckValueInRange(
    UMyCustomAsset* Asset,
    float MinValue,
    float MaxValue)
{
    FInterchangeTestFunctionResult Result;

    if (!Asset)
    {
        Result.AddError(TEXT("Asset is null"));
        return Result;
    }

    float Value = Asset->GetCustomValue();
    if (Value < MinValue || Value > MaxValue)
    {
        Result.AddError(FString::Printf(
            TEXT("Asset value %f is outside expected range [%f, %f]"),
            Value, MinValue, MaxValue));
    }

    return Result;
}
```

## 模块依赖

本插件为测试专用插件，依赖 Interchange 核心模块和引擎自动化测试基础设施。

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 核心接口和数据结构 |
| `InterchangeEngine` | Interchange 导入/导出引擎 |
| `InterchangePipelines` | Interchange 导入管线 |
| `InterchangeNodes` | Interchange 节点类型定义 |
| `AutomationTest` | UE 自动化测试框架 |
| `AutomationController` | 自动化测试控制器 |
| `ImageWriteQueue` | 截图对比功能的图像写入 |
| `FunctionalTesting` | 功能测试基础设施 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新的 UE_LOGF 格式 |
| 2026-04-06 | `a3591f26` | [ContentBrowser] New Add Menu Interchange Menu | Content Browser 新增 Interchange 菜单项 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd... | 废弃旧的对象遍历函数，引入新 API |
| 2026-03-18 | `44060456` | Interchange - Added support for import containing both SM and SKM at the same time. | 新增同时导入静态网格和骨骼网格的支持 |
| 2026-03-04 | `7ceb4698` | Interchange - New Skeletal Mesh Combine Options | 新增骨骼网格合并选项的测试支持 |

### 维护评价

- **创建时间**：2022 年 2 月，约 4 年历史
- **实验性标记**：`IsBetaVersion=true`，仍处于 Beta 阶段
- **更新频率**：2026 年 3-4 月期间有多次提交，保持活跃更新
- **更新内容**：近期更新包括新功能支持（同时导入 SM/SKM、骨骼网格合并选项）、代码现代化（UE_LOGF 迁移）和 API 清理
- **维护状态**：**活跃维护中** — 作为 Interchange 系统的核心测试基础设施，随 Interchange 框架同步演进
- **推荐程度**：如果你在开发或维护 Interchange 相关功能，强烈推荐使用此框架编写回归测试。对于不涉及 Interchange 的项目则无需关注

**注意**：由于 `IsBetaVersion=true`，API 和测试计划格式可能会在后续版本中发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/InterchangeTests)
- 官方文档：无
- 测试用例：本插件本身即为测试框架，测试计划以 JSON 文件形式定义在 `ImportTestsPath` 配置的目录中