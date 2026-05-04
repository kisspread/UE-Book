# Editor Tests

> 

| 属性 | 值 |
|---|---|
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源：FBX 模型、自动重导入脚本、图片） |
| 模块 | `EditorTests` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2016-09-21 |
| 年龄标签 | 👴 老古董（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/EditorTests) | |

## 用途

EditorTests 是 Epic Games 内部使用的 **编辑器自动化测试插件**，为 Unreal Editor 的核心功能提供全面的回归测试和冒烟测试。它不是一个给最终用户使用的功能插件，而是一个纯粹的测试套件，覆盖了编辑器中几乎所有关键工作流：资产导入（FBX、通用格式）、蓝图编译、地图加载、碰撞检测、光照构建、Mesh 操作、源码控制集成等。

该插件默认禁用（`EnabledByDefault: false`），通常只在 CI/CD 管线或 QA 手动测试时启用。

## 使用场景

- **CI 回归测试**：在 nightly build 中运行 `Editor.Import`、`Project.Blueprints.Compile Blueprints` 等测试，确保编辑器功能不被破坏
- **QA 验证**：QA 团队通过 Session Frontend 面板选择性运行特定测试（如 `Editor.Import.Fbx`）来验证特定功能
- **蓝图编辑器测试**：验证所有项目蓝图能正确编译、没有断开的节点
- **资产管线验证**：确认 FBX 导入、自动重导入等功能正常工作
- **性能基准**：通过 `Editor.Performance.Capture` 测试采集编辑器性能数据

## 蓝图用法

EditorTests 提供了 `UEditorUtilityTest` 基类，允许通过蓝图创建编辑器测试，以及 `UEditorTestsUtilityLibrary` 提供的测试辅助函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BakeMaterialsForComponent` | 为静态网格组件烘焙材质 | `UEditorTestsUtilityLibrary` |
| `MergeStaticMeshComponents` | 合并多个静态网格组件并烘焙图集材质 | `UEditorTestsUtilityLibrary` |
| `CreateProxyMesh` | 为静态网格组件创建简化代理网格 | `UEditorTestsUtilityLibrary` |
| `GetChildEditorWidgetByName` | 按名称查找编辑器 Widget | `UEditorTestsUtilityLibrary` |
| `SetEditorWidgetNavigationRule` | 设置 Widget 导航规则 | `UEditorTestsUtilityLibrary` |
| `GetEditorWidgetNavigationRule` | 获取 Widget 导航规则 | `UEditorTestsUtilityLibrary` |

### EditorUtilityTest 蓝图测试框架

`UEditorUtilityTest` 是一个 `Blueprintable` 的 UObject 子类，允许通过蓝图创建完整的自动化测试：

| 节点 | 说明 |
|---|---|
| `OnTestPrepare` | 委托：测试准备阶段触发 |
| `OnTestStart` | 委托：测试开始时触发 |
| `OnTestFinished` | 委托：测试完成时触发，返回 `EEditorUtilityTestResult` |
| `Run()` | 启动测试 |
| `FinishPrepareTest()` | 准备完成，开始执行 |
| `FinishTest(State, Message)` | 结束测试并报告结果 |
| `ExpectTrue(Condition, ErrorMessage)` | 断言条件为真 |
| `ExpectFalse(Condition, ErrorMessage)` | 断言条件为假 |
| `AddError/Warning/Info` | 添加测试日志消息 |
| `Owner` | 测试负责组（如 "Editor"、"Rendering"） |
| `Description` | 测试描述 |
| `PreparationTimeLimit` | 准备阶段超时（0 = 无限制） |
| `TimeLimit` | 运行阶段超时（0 = 无限制） |

### 使用示例（蓝图描述）

1. 创建一个 `EditorUtilityTest` 蓝图子类
2. 在 `OnTestPrepare` 事件中设置测试环境（加载地图、创建 Actor 等），最后调用 `FinishPrepareTest()`
3. 在 `OnTestStart` 事件中执行实际测试逻辑，使用 `ExpectTrue/ExpectFalse` 进行断言
4. 调用 `FinishTest(EEditorUtilityTestResult::Succeeded, "Test passed")` 完成测试

## C++ 用法

EditorTests 的主要价值在于其自动化测试用例，这些测试展示了如何使用 UE5 的自动化测试框架编写编辑器测试。

### 头文件引入

```cpp
#include "Misc/AutomationTest.h"
#include "Tests/AutomationEditorCommon.h"
#include "Tests/AutomationCommon.h"
```

### 基本用法 — 简单自动化测试

使用 `IMPLEMENT_SIMPLE_AUTOMATION_TEST` 宏创建单个测试用例。

```cpp
// 来源: Source/EditorTests/Private/UnrealEd/EditorAutomationTests.cpp
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FReinitializeRHIResources,
    "System.Engine.Rendering.Reinit Resources",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter
);

bool FReinitializeRHIResources::RunTest(const FString& Parameters)
{
    GEditor->Exec(NULL, TEXT("ReinitRHIResources"));
    return true;
}
```

### 基本用法 — 复杂参数化测试

使用 `IMPLEMENT_COMPLEX_AUTOMATION_TEST` 宏创建参数化测试，通过 `GetTests()` 枚举子测试。

```cpp
// 来源: Source/EditorTests/Private/UnrealEd/EditorAutomationTests.cpp
IMPLEMENT_COMPLEX_AUTOMATION_TEST(
    FLoadAllMapsInEditorTest,
    "Project.Maps.Load All In Editor",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::StressFilter
);

void FLoadAllMapsInEditorTest::GetTests(
    TArray<FString>& OutBeautifiedNames,
    TArray<FString>& OutTestCommands) const
{
    TArray<FString> FileList;
    FEditorFileUtils::FindAllPackageFiles(FileList);

    for (int32 FileIndex = 0; FileIndex < FileList.Num(); FileIndex++)
    {
        const FString& Filename = FileList[FileIndex];
        if (FPaths::GetExtension(Filename, true) == FPackageName::GetMapPackageExtension())
        {
            if (FAutomationTestFramework::Get().ShouldTestContent(Filename))
            {
                if (!Filename.Contains(TEXT("/Engine/")))
                {
                    OutBeautifiedNames.Add(FPaths::GetBaseFilename(Filename));
                    OutTestCommands.Add(Filename);
                }
            }
        }
    }
}

bool FLoadAllMapsInEditorTest::RunTest(const FString& Parameters)
{
    FString MapName = Parameters;
    FAutomationEditorCommonUtils::LoadMap(MapName);
    return true;
}
```

### 进阶用法 — 潜伏命令（Latent Commands）

测试中使用 `DEFINE_LATENT_AUTOMATION_COMMAND` 定义异步操作，适用于需要等待帧更新的场景。

```cpp
// 来源: Source/EditorTests/Private/UnrealEd/EditorAutomationTests.cpp
struct PointLightParameters
{
    APointLight* PointLight;
    float LightBrightness;
    float LightRadius;
    FVector LightLocation;
    FColor LightColor;
};

DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(
    PointLightUpdateCommand, PointLightParameters, PointLightUsing);

bool PointLightUpdateCommand::Update()
{
    PointLightUsing.PointLight->SetMobility(EComponentMobility::Movable);
    PointLightUsing.PointLight->SetBrightness(PointLightUsing.LightBrightness);
    PointLightUsing.PointLight->SetLightColor(PointLightUsing.LightColor);
    PointLightUsing.PointLight->TeleportTo(PointLightUsing.LightLocation, FRotator(0, 0, 0));
    PointLightUsing.PointLight->SetRadius(PointLightUsing.LightRadius);
    return true;
}
```

### 进阶用法 — 蓝图编译回归测试

验证项目中所有蓝图能正确编译。

```cpp
// 来源: Source/EditorTests/Private/UnrealEd/BlueprintAutomationTests.cpp
IMPLEMENT_COMPLEX_AUTOMATION_TEST(
    FCompileBlueprintsTest,
    "Project.Blueprints.Compile Blueprints",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::StressFilter
);
```

## 测试用例分类

该插件包含以下测试类，覆盖编辑器核心功能：

| 测试路径 | 测试类 | 测试内容 |
|---|---|---|
| `Editor.Import` | `FGenericImportAssetsAutomationTest` | 通用资产导入 |
| `Editor.Import.Fbx` | `FFbxImportAssetsAutomationTest` | FBX 文件导入/重导入 |
| `Editor.Meshes.MeshDescription` | `FMeshDescriptionAutomationTest` | MeshDescription API |
| `Editor.Content.FeaturePackValidityTest` | `FFeaturePackValidityTest` | Feature Pack 验证 |
| `Project.Maps.Load All In Editor` | `FLoadAllMapsInEditorTest` | 加载所有地图 |
| `Project.Blueprints.Compile Blueprints` | `FCompileBlueprintsTest` | 编译所有蓝图 |
| `Project.Blueprints.Compile Anims` | `FCompileAnimBlueprintsTest` | 编译动画蓝图 |
| `Project.Editor.Open Assets` | `FOpenAssetEditors` | 打开资产编辑器 |
| `Project.Iteration.PIE` | `FIterationOpenAssets` | PIE 迭代测试 |
| `System.Engine.Rendering.Reinit Resources` | `FReinitializeRHIResources` | RHI 资源重初始化 |
| `System.QA.Mesh Factory Validation` | `FStaticMeshValidation` | 静态网格工厂验证（已禁用） |
| `System.QA.Convert Meshes` | `FConvertToValidation` | BSP/网格转换（已禁用） |
| `System.Promotion.Editor.Settings.Keybindings` | `FEditorSettingsKeybindingsTest` | 快捷键设置 |
| `System.Promotion.Editor.Settings.Preferences` | `FEditorSettingsPreferencesTest` | 编辑器偏好设置 |

此外还包括：碰撞测试、光照测试、编辑器性能采集、源码控制集成测试、几何体画刷测试、自动重导入测试、动画蓝图 Fast Path 测试、ObjectTools 删除引用测试等。

## Demo 示例

### 创建一个简单的编辑器自动化测试

```cpp
// MyEditorTest.h
#pragma once
#include "Misc/AutomationTest.h"

// 声明一个简单的编辑器自动化测试
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FMyCustomEditorTest,
    "Project.MyTests.CustomEditorTest",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter
);
```

```cpp
// MyEditorTest.cpp
#include "MyEditorTest.h"
#include "Tests/AutomationEditorCommon.h"
#include "Editor.h"

bool FMyCustomEditorTest::RunTest(const FString& Parameters)
{
    // 创建一个新地图
    UWorld* World = FAutomationEditorCommonUtils::CreateNewMap();

    // 验证世界创建成功
    TestNotNull(TEXT("World should be created"), World);

    // 添加一个 Actor
    FActorSpawnParameters SpawnParams;
    AActor* TestActor = World->SpawnActor<AActor>(AActor::StaticClass(), SpawnParams);

    // 验证 Actor 创建成功
    TestNotNull(TEXT("Actor should be spawned"), TestActor);

    // 验证 Actor 在世界中
    TestEqual(TEXT("World should have actors"), World->GetCurrentLevel()->Actors.Num() > 1, true);

    return true;
}
```

**Build.cs 依赖说明**：如果要在自己的模块中编写类似的编辑器测试，需要在 `Build.cs` 中添加：

```csharp
PrivateDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "UnrealEd",
    "AutomationController"
});
```

## 模块依赖

该插件的 `Build.cs` 声明了大量依赖，因为它需要测试编辑器的方方面面：

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础库（Public 依赖） |
| `UnrealEd` | 编辑器核心框架 |
| `Engine` | 引擎核心（Actor、World、StaticMesh 等） |
| `CoreUObject` | UObject 系统 |
| `AssetTools` | 资产导入/管理工具 |
| `SourceControl` | 源码控制集成 |
| `BlueprintGraph` | 蓝图图表编辑 |
| `Kismet2` | 蓝图编译和编辑工具（通过 UnrealEd 间接依赖） |
| `MaterialEditor` | 材质编辑器 |
| `MeshDescription` | 网格描述 API |
| `MeshBuilder` | 网格构建器 |
| `NavigationSystem` | 导航系统 |
| `Slate` / `SlateCore` | UI 框架 |
| `AutomationController` | 自动化测试控制器 |
| `Blutility` | 蓝图工具（Editor Utility） |
| `UMG` / `UMGEditor` | UMG UI 编辑器 |
| `RenderCore` / `RHI` | 渲染核心和硬件接口 |
| `AnimGraphRuntime` | 动画图运行时 |
| `DirectoryWatcher` | 文件系统监控（自动重导入测试） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-08-21 | `2c158c4d` | 重构 `GetUsedTextures` MaterialInterface 使用 TOptional 参数，覆盖 EditorTests 中的材质烘焙测试代码 |
| 2025-07-14 | `8c4cad91` | StaticMesh 的 `WITH_EDITORONLY_DATA` 属性改为访问器模式，SkeletalMesh 同步调整 |
| 2025-06-18 | `08316dbb` | MaterialResource 缓存 ShaderPlatform，影响材质烘焙相关测试 |

### 维护评价

- **创建时间**：2016 年 9 月，已存在约 10 年
- **最近更新**：最近 3 次提交均为引擎底层 API 的同步适配（材质、网格访问器变更），不是针对 EditorTests 插件本身的功能更新
- **维护状态**：被动维护 — 当引擎核心 API 变更时需要同步更新，但没有主动的功能增强
- **已知限制**：
  - 部分测试标记为 `Disabled`（如 `FStaticMeshValidation`、`FConvertToValidation`），说明某些测试路径可能已过时
  - 测试依赖大量编辑器内部类，难以在独立环境中运行
  - 需要非空 RHI（`NonNullRHI` 标志），不能在纯命令行模式运行
- **推荐使用**：作为 Epic 内部 QA 流程的一部分，该插件持续被维护。如果你在构建自定义引擎版本并需要验证编辑器功能完整性，可以启用此插件运行测试。普通游戏开发者不需要直接使用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/EditorTests)
- [测试资源](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/EditorTests/Content/Editor/AutoReimport)（自动重导入测试脚本和资源）
