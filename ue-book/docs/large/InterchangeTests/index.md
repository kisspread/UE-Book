# Interchange Tests

> Plugin for Interchange automation tests.

| 属性 | 值 |
|---|---|
| 分类 | Testing |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeTests` (Editor), `InterchangeTestEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-02-20 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/InterchangeTests) | |

## 用途

Interchange Tests 是 UE5 Interchange 资产导入框架的**数据驱动自动化测试框架**。它提供了一套完整的测试基础设施，用于验证通过 Interchange 管线导入各种资产类型（静态网格、骨骼网格、材质、纹理、动画、灯光、关卡序列等）后的结果是否正确。

该插件解决的核心问题是：Interchange 作为 UE5 的新一代资产导入/导出管线，需要一个标准化的方式来回归测试导入结果。与传统的硬编码自动化测试不同，Interchange Tests 使用**测试计划资产（Test Plan Asset）**来定义测试流程，测试计划可以在编辑器中可视化编辑，并通过 JSON 序列化进行版本管理。

### 架构概览

```
UInterchangeImportTestPlan          ← 测试计划（资产形式）
├── UInterchangeImportTestStepImport   ← 导入步骤
│   ├── SourceFile                       源文件路径
│   ├── PipelineStack                    覆盖管线栈
│   └── Tests[]                          验证函数列表
└── UInterchangeImportTestStepReimport[] ← 重导入步骤栈
    ├── SourceFileToReimport             重导入源文件
    └── Tests[]                          验证函数列表
```

每个验证函数（`FInterchangeTestFunction`）绑定到一个资产类型和一个 `UFUNCTION(Exec)` 检查函数，通过反射机制动态调用。测试函数类按资产类型组织，形成一个可扩展的验证库。

## 使用场景

- 你在开发或修改 Interchange 导入管线，需要验证导入结果不会回归 → 创建 Test Plan 资产并添加到自动化测试套件
- 你需要为新的 3D 格式（如 glTF、USD）编写导入测试 → 继承 `UImportTestFunctionsBase` 并添加新的验证函数
- 你需要验证导入后的资产属性（LOD 数量、顶点数、材质槽等）是否正确 → 在 Test Plan 中配置 `FInterchangeTestFunction`
- 你需要测试重导入工作流（修改源文件后重新导入） → 在 Test Plan 的 ReimportStack 中添加重导入步骤
- 你需要对导入结果进行截图比对 → 启用 Screenshot Comparison 并配置相机参数

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RunThisTest` | 在编辑器中立即运行当前测试计划 | `UInterchangeImportTestPlan` |
| `GetPipelinePropertiesAsJSON` | 将管线属性导出为 JSON 字符串 | `UInterchangeTestsBlueprintFunctionLibrary` |

### 使用示例（蓝图描述）

Interchange Tests 主要通过编辑器 UI 操作，而非蓝图节点。典型工作流：

1. 在 Content Browser 中右键 → 创建 `InterchangeImportTestPlan` 资产
2. 在 Details 面板中配置 Import Step：指定源文件、管线栈、验证函数
3. 可选添加 Reimport Step：指定重导入源文件和额外验证
4. 点击 "Run This Test" 按钮立即执行，或通过 Automation Window 批量运行

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeImportTestPlan.h"
#include "InterchangeImportTestStepImport.h"
#include "InterchangeImportTestStepReimport.h"
#include "InterchangeTestFunction.h"
#include "ImportTestFunctions/StaticMeshImportTestFunctions.h"
```

### 基本用法：创建验证函数

验证函数是标记为 `UFUNCTION(Exec)` 的静态函数，接收被测资产和期望参数，返回 `FInterchangeTestFunctionResult`。

**来源**: `Source/InterchangeTests/Public/ImportTestFunctions/StaticMeshImportTestFunctions.h`

```cpp
// 验证导入的静态网格 LOD 数量
UFUNCTION(Exec)
static FInterchangeTestFunctionResult CheckLodCount(
    UStaticMesh* Mesh, 
    int32 ExpectedNumberOfLods
);

// 验证顶点数
UFUNCTION(Exec)
static FInterchangeTestFunctionResult CheckVertexCount(
    UStaticMesh* Mesh, 
    int32 LodIndex, 
    int32 ExpectedNumberOfVertices
);

// 验证材质槽数量
UFUNCTION(Exec)
static FInterchangeTestFunctionResult CheckMaterialSlotCount(
    UStaticMesh* Mesh, 
    int32 ExpectedNumberOfMaterialSlots
);
```

### 基本用法：与 Ground Truth 对比

**来源**: `Source/InterchangeTests/Public/ImportTestFunctions/StaticMeshImportTestFunctions.h`

```cpp
// 将导入结果与已知正确的资产进行对比
UFUNCTION(Exec)
static FInterchangeTestFunctionResult CheckAgainstGroundTruth(
    UStaticMesh* Mesh, 
    TSoftObjectPtr<UStaticMesh> MeshToCompare,
    bool bCheckVertexCountEqual = true,
    bool bCheckTriangleCountEqual = true,
    bool bCheckUVChannelCountEqual = true,
    bool bCheckCollisionPrimitiveCountEqual = true,
    bool bCheckVertexPositionsEqual = true,
    bool bCheckNormalsEqual = true
);
```

### 进阶用法：自定义测试函数类

要为新的资产类型添加验证能力，继承 `UImportTestFunctionsBase`：

**来源**: `Source/InterchangeTests/Public/ImportTestFunctions/ImportTestFunctionsBase.h`

```cpp
UCLASS(MinimalAPI)
class UMyAssetImportTestFunctions : public UImportTestFunctionsBase
{
    GENERATED_BODY()

public:
    virtual UClass* GetAssociatedAssetType() const override
    {
        return UMyAsset::StaticClass();
    }

    // 所有验证函数必须标记为 UFUNCTION(Exec)
    UFUNCTION(Exec)
    static FInterchangeTestFunctionResult CheckMyProperty(
        UMyAsset* Asset, 
        float ExpectedValue
    );
};
```

### 进阶用法：测试计划的 JSON 序列化

**来源**: `Source/InterchangeTests/Public/InterchangeImportTestPlan.h`

```cpp
UInterchangeImportTestPlan* TestPlan = NewObject<UInterchangeImportTestPlan>();

// 序列化到 JSON 文件
TestPlan->WriteToJson(TEXT("/path/to/test_plan.json"));

// 从 JSON 文件反序列化
TestPlan->ReadFromJson(TEXT("/path/to/test_plan.json"));
```

## Demo 示例

### 最小测试函数实现

```cpp
// MyAssetImportTestFunctions.h
#pragma once
#include "ImportTestFunctions/ImportTestFunctionsBase.h"
#include "MyAssetImportTestFunctions.generated.h"

UCLASS(MinimalAPI)
class UMyAssetImportTestFunctions : public UImportTestFunctionsBase
{
    GENERATED_BODY()
public:
    virtual UClass* GetAssociatedAssetType() const override;

    UFUNCTION(Exec)
    static FInterchangeTestFunctionResult CheckVertexCount(
        UStaticMesh* Mesh, int32 LodIndex, int32 ExpectedCount);
};

// MyAssetImportTestFunctions.cpp
#include "MyAssetImportTestFunctions.h"
#include "InterchangeTestFunction.h"

UClass* UMyAssetImportTestFunctions::GetAssociatedAssetType() const
{
    return UStaticMesh::StaticClass();
}

FInterchangeTestFunctionResult UMyAssetImportTestFunctions::CheckVertexCount(
    UStaticMesh* Mesh, int32 LodIndex, int32 ExpectedCount)
{
    FInterchangeTestFunctionResult Result;
    if (!Mesh)
    {
        Result.AddError(TEXT("Mesh is null"));
        return Result;
    }
    
    const FMeshDescription* MeshDesc = Mesh->GetMeshDescription(LodIndex);
    if (!MeshDesc)
    {
        Result.AddError(FString::Printf(TEXT("No mesh description for LOD %d"), LodIndex));
        return Result;
    }
    
    int32 ActualCount = MeshDesc->Vertices().Num();
    if (ActualCount != ExpectedCount)
    {
        Result.AddError(FString::Printf(
            TEXT("Expected %d vertices, got %d"), ExpectedCount, ActualCount));
    }
    return Result;
}
```

**Build.cs 依赖**:

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core", "CoreUObject", "Engine", "Json", "JsonUtilities"
});
PrivateDependencyModuleNames.AddRange(new string[] {
    "InterchangeCore", "InterchangeEngine", "InterchangePipelines",
    "MeshDescription", "StaticMeshDescription"
});
```

## 模块依赖

### InterchangeTests 模块

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和容器 |
| `CoreUObject` | UObject 反射系统 |
| `Engine` | 引擎核心类型 |
| `Json` | JSON 解析（测试计划序列化） |
| `JsonUtilities` | JSON 工具函数 |
| `InterchangeCore` | Interchange 核心接口 |
| `InterchangeEngine` | Interchange 导入引擎 |
| `InterchangePipelines` | Interchange 管线系统 |
| `InterchangeDispatcher` | Interchange 进程调度 |
| `MeshDescription` | 网格数据描述 |
| `StaticMeshDescription` | 静态网格描述 |
| `SkeletalMeshDescription` | 骨骼网格描述 |
| `FunctionalTesting` | 功能测试框架 |
| `VariantManagerContent` | 变体管理器内容 |
| `LevelSequence` | 关卡序列 |
| `MovieScene` | 影视场景 |
| `UnrealEd` | 编辑器核心 |

### InterchangeTestEditor 模块

| 模块 | 用途 |
|---|---|
| `InterchangeTests` | 测试核心模块 |
| `InterchangeCore` | Interchange 核心接口 |
| `PropertyEditor` | 属性面板编辑器 |
| `ContentBrowser` | 内容浏览器集成 |
| `ToolMenus` | 工具菜单系统 |
| `AssetDefinition` | 资产定义系统 |
| `AssetTools` | 资产工具 |
| `SlateCore` / `Slate` | UI 框架 |
| `AutomationTest` | 自动化测试框架 |

## 架构详解

### 测试计划（Test Plan）

`UInterchangeImportTestPlan` 是测试的核心资产，包含：

- **Description**: 测试描述文本
- **WorldPath**: 用于截图测试的关卡路径
- **ImportStep**: 单个导入步骤（`UInterchangeImportTestStepImport`）
- **ReimportStack**: 重导入步骤数组（`UInterchangeImportTestStepReimport[]`）

### 导入步骤（Import Step）

`UInterchangeImportTestStepImport` 定义一次导入操作：

| 属性 | 说明 |
|---|---|
| `SourceFile` | 源文件路径（相对于 JSON 脚本） |
| `bUseOverridePipelineStack` | 是否使用覆盖管线栈 |
| `PipelineStack` | 覆盖管线栈（空则使用默认） |
| `PipelineSettings` | 管线设置覆盖 |
| `bEmptyDestinationFolderPriorToImport` | 导入前清空目标文件夹 |
| `bImportIntoLevel` | 是否使用导入到关卡工作流 |
| `bTakeScreenshot` | 是否进行截图比对 |
| `ScreenshotParameters` | 截图参数（相机位置/自动对焦等） |
| `Tests` | 验证函数数组（继承自基类） |

### 重导入步骤（Reimport Step）

`UInterchangeImportTestStepReimport` 在导入步骤之后执行，可指定不同的源文件和管线：

| 属性 | 说明 |
|---|---|
| `SourceFileToReimport` | 重导入源文件路径 |
| `AssetTypeToReimport` | 要重导入的资产类型 |
| `AssetNameToReimport` | 要重导入的资产名称（同类型多个时使用） |
| `bImportIntoLevel` | 是否为关卡导入重导入 |
| `bTakeScreenshot` | 是否截图比对 |

### 验证函数系统（Test Function）

`FInterchangeTestFunction` 是验证的核心结构：

| 属性 | 说明 |
|---|---|
| `AssetClass` | 被测资产的 UClass |
| `OptionalAssetName` | 可选的资产名称（多个同类资产时） |
| `CheckFunction` | 要调用的 UFunction 指针 |
| `Parameters` | 参数名→值的映射（文本形式） |

验证函数通过 UE 反射系统调用：`FInterchangeTestFunction::Invoke()` 将文本参数反序列化为二进制，调用目标 UFunction，收集返回的 `FInterchangeTestFunctionResult`。

### 自动化执行流程

**来源**: `Source/InterchangeTests/Private/InterchangeImportTest.cpp`

1. `FInterchangeImportTest::GetTests()` 扫描资产注册表中所有 `UInterchangeImportTestPlan` 资产
2. `FInterchangeImportTest::RunTest()` 对每个测试计划：
   - 清理临时目录 `/Game/Tests/Interchange/Temp/ImportTest/`
   - 设置关卡（如果需要导入到关卡）
   - 执行 ImportStep → 收集结果 → 执行验证 → 可选截图
   - 遍历 ReimportStack → 每步执行重导入 → 收集结果 → 验证 → 可选截图
   - 清理并报告结果

### 验证函数库

插件提供以下资产类型的验证函数：

| 类 | 资产类型 | 验证能力 |
|---|---|---|
| `UStaticMeshImportTestFunctions` | `UStaticMesh` | LOD 数、顶点/三角形/UV 数、材质槽、Socket、碰撞体、Nanite 设置、包围盒、Ground Truth 对比 |
| `USkeletalMeshImportTestFunctions` | `USkeletalMesh` | LOD 数、顶点/三角形数、材质槽、骨骼数/位置、Morph Target、蒙皮权重 |
| `UTextureImportTestFunctions` | `UTexture` | 纹理数量、过滤模式、寻址模式（X/Y/Z） |
| `UMaterialImportTestFunctions` | `UMaterialInterface` | 材质数量、Shading Model、Blend Mode、双面、标量/向量参数 |
| `UMaterialXTestFunctions` | `UMaterialInterface` | MaterialX StandardSurface 输入连接数和连接状态 |
| `UAnimationImportTestFunctions` | `UAnimSequence` | 动画数量、长度、帧数、曲线关键帧时间/值/切线 |
| `ULevelSequenceImportTestFunctions` | `ULevelSequence` | 序列数量、长度、区段数、插值模式 |
| `ULevelVariantSetsImportTestFunctions` | `ULevelVariantSets` | 变体集数量、变体数量、绑定数量 |
| `UActorImportTestFunctions` | `AActor` | Actor 数量/类型、属性值（支持正则）、组件属性值 |
| `ULightImportTestFunctions` | `ALight` | 灯光位置/方向/强度/颜色 |
| `UPointLightImportTestFunctions` | `APointLight` | 衰减指数 |
| `USpotLightImportTestFunctions` | `ASpotLight` | 内锥角/外锥角 |
| `UInterchangeResultImportTestFunctions` | `UInterchangeResultsContainer` | 导入过程中是否生成了特定类型的错误/警告 |
| `UAssetImportTestFunctions` | `UObject` | 元数据数量/键/值、对象路径子串匹配 |

### Latent Automation Commands

测试执行使用 UE 的延迟自动化命令系统：

| 命令 | 说明 |
|---|---|
| `FInterchangeIntializeStepCommand` | 初始化测试步骤（设置导入/重导入上下文） |
| `FInterchangeInterStepCollectResultCommand` | 收集导入结果 |
| `FInterchangeSetupScreenshotViewportCommand` | 设置截图视口（相机位置/对焦） |
| `FInterchangeCaptureScreenshotCommand` | 捕获并比对截图 |
| `FInterchangeInterStepPerformTestsAndCollectGarbageCommand` | 执行验证函数并触发 GC |
| `FInterchangeTestAutomationTestSuccessCommand` | 报告测试成功/失败 |
| `FInterchangeTestCleanUpCommand` | 清理临时文件和关卡 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-14 | `8c4cad9` | Changed all WITH_EDITORONLY_DATA properties in StaticMesh to have accessors | 引擎级重构，将 StaticMesh 的编辑器专用数据改为访问器模式，InterchangeTests 跟随适配 |
| 2025-07-10 | `9803c44` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 代码质量改进，优化编译时间 |
| 2025-05-30 | `2739c3d` | Updated headers using UnrealCodeFixup for dllstorage | DLL 导出宏规范化，无功能变化 |

### 维护评价

- **创建时间**: 2022-02-20，随 UE5 Interchange 框架一同诞生
- **最近更新**: 2025-07-14，最近的更新均为引擎级代码质量维护，非功能性变更
- **维护状态**: 维护中 — 作为 Epic 内部测试基础设施持续跟随引擎更新
- **已知限制**:
  - ⚠️ Mac 和 Linux 平台因 InterchangeWorker 问题无法运行自动化测试（代码中有 `#if PLATFORM_MAC || PLATFORM_LINUX return;`）
  - 标记为 `IsBetaVersion: true`，API 可能随 Interchange 框架演进而变化
- **推荐程度**: 如果你在开发 Interchange 管线或需要验证导入结果，这是唯一的选择；否则作为测试插件可忽略

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/InterchangeTests)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/InterchangeTests/Source/InterchangeTests/Private)（测试执行逻辑在 `InterchangeImportTest.cpp`）
