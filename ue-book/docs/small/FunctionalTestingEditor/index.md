# Functional Testing Editor

> Functional Testing Editor 的编辑器集成模块，为 UE 功能测试框架提供编辑器 UI 支持。

| 属性 | 值 |
|---|---|
| 分类 | Testing |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | FunctionalTestingEditor (Editor) |
| 创建时间 | 2016-10-05 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/FunctionalTestingEditor) | |

## 用途

FunctionalTestingEditor 是 UE 功能测试框架（FunctionalTesting）的**编辑器侧配套插件**。FunctionalTesting 插件本身负责运行时测试执行，而本插件专注于编辑器集成：

1. **在 Tools 菜单中添加 "Test Automation" 入口**，点击可打开 Session Frontend 的 Automation 面板
2. **在 Placement Mode 中注册测试 Actor 类别**，方便拖拽放置 `AFunctionalTest` 和 `AScreenshotFunctionalTest`
3. **注册 Ground Truth Data 资产类型**，支持在 Content Browser 中创建和编辑用于截图比对的基准数据资产
4. **提供 Editor-only 版本的功能测试 Actor**（`AEditorFunctionalTest`、`AEditorScreenshotFunctionalTest`），用于需要调用编辑器专属蓝图的测试场景
5. **注册控制台命令 `Automate.OpenMapAndFocusActor`**，自动化流程可用此命令打开地图并聚焦到指定 Actor

本插件 **默认未启用**（`EnabledByDefault: false`），需要在 Editor Preferences → Plugins 中手动启用，或在 `.uproject` 中显式声明。

## 使用场景

- 你在编写自动化功能测试，需要在编辑器中方便地放置 FunctionalTest Actor → 启用本插件，通过 Placement Mode 的 "Testing" 类别拖拽放置
- 你需要进行截图基准测试（Screenshot Functional Test），需要管理 Ground Truth Data 资产 → 本插件提供资产工厂和编辑器支持
- 你的功能测试需要调用编辑器专属蓝图（如编辑器 Utility Widget 等）→ 继承 `AEditorFunctionalTest` 而非 `AFunctionalTest`
- 你需要在自动化管线中打开特定地图并聚焦到某个 Actor → 使用 `Automate.OpenMapAndFocusActor` 控制台命令

## 蓝图用法

本插件不直接暴露 BlueprintCallable 函数。其核心作用是提供 **可在蓝图中继承的测试 Actor 基类**。

### 核心类

| 类 | 说明 | 继承自 |
|---|---|---|
| `AEditorFunctionalTest` | Editor-only 功能测试 Actor，蓝图可继承 | `AFunctionalTest` |
| `AEditorScreenshotFunctionalTest` | Editor-only 截图功能测试 Actor | `AScreenshotFunctionalTest` |

### 使用示例（蓝图描述）

1. 在 Content Browser 中右键 → Miscellaneous → 创建 Blueprint Class
2. 选择父类 `EditorFunctionalTest`（而非 `FunctionalTest`）
3. 在蓝图中实现 `Prepare Test`、`Start Test`、`On Test Finished` 等逻辑
4. 将 Actor 拖入测试关卡，使用 Session Frontend 的 Automation 面板运行

## C++ 用法

### 头文件引入

```cpp
#include "EditorFunctionalTest.h"
```

### 基本用法：继承 Editor-only 测试 Actor

当你的功能测试需要访问编辑器 API 时，应继承 `AEditorFunctionalTest` 而非 `AFunctionalTest`：

```cpp
// Source: Engine/Plugins/Tests/FunctionalTestingEditor/Source/Public/EditorFunctionalTest.h
// AEditorFunctionalTest 重写了 IsEditorOnly() 和 IsEditorOnlyLoadedInPIE() 返回 true

UCLASS(Blueprintable)
class AMyEditorTest : public AEditorFunctionalTest
{
    GENERATED_BODY()
    // 可以安全调用编辑器专属 API
    virtual void StartTest() override
    {
        // 测试逻辑...
        FinishTest(EFunctionalTestResult::Succeeded, TEXT("OK"));
    }
};
```

### 使用控制台命令进行自动化

`Automate.OpenMapAndFocusActor` 命令接受两个参数：地图资产路径和 Actor 名称。

```cpp
// Source: Engine/Plugins/Tests/FunctionalTestingEditor/Source/Private/FunctionalTestingEditorModule.cpp
// 控制台命令注册方式：
// Automate.OpenMapAndFocusActor /Game/Maps/TestMap.MyTestMap BP_TestActor_0

// 在自动化脚本中调用：
IConsoleManager::Get().ProcessConsoleCommand(
    TEXT("Automate.OpenMapAndFocusActor"),
    {TEXT("/Game/Maps/TestMap"), TEXT("BP_TestActor_0")}
);
```

### 进阶用法：Ground Truth Data

本插件注册了 `UGroundTruthDataFactory`，支持在 Content Browser 中创建 `UGroundTruthData` 资产。这些资产用于存储截图基准数据，配合 `AScreenshotFunctionalTest` 进行视觉回归测试。

```cpp
// 资产工厂定义：Source/Private/GroundTruthDataFactory.h
// 创建新的 Ground Truth Data 资产（通常通过编辑器 UI，也可代码创建）
UGroundTruthData* GroundTruthData = NewObject<UGroundTruthData>(
    InParent, UGroundTruthData::StaticClass(), InName, RF_Transactional
);
```

## Demo 示例

一个最小的 Editor-only 功能测试示例：

```cpp
// MyEditorTest.h
#pragma once
#include "EditorFunctionalTest.h"
#include "MyEditorTest.generated.h"

UCLASS(Blueprintable)
class AMyEditorTest : public AEditorFunctionalTest
{
    GENERATED_BODY()

    virtual void StartTest() override
    {
        Super::StartTest();
        // 这里可以安全使用编辑器 API
        FinishTest(EFunctionalTestResult::Succeeded, TEXT("Editor test passed"));
    }
};
```

Build.cs 依赖：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "FunctionalTesting"
});
```

## 模块依赖

从 Build.cs 的 `PublicDependencyModuleNames` 提取。如果要使用本插件提供的类，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `InputCore` | 输入系统核心 |
| `CoreUObject` | UObject 系统 |
| `SlateCore` | Slate UI 核心（编辑器 UI） |
| `Slate` | Slate UI 框架 |
| `Engine` | 引擎核心（包含 FunctionalTest 基类） |
| `AssetRegistry` | 资产注册表（用于资产查找） |

Private 依赖（插件内部使用，使用者无需关心）：`FunctionalTesting`、`UnrealEd`、`LevelEditor`、`SessionFrontend`、`PlacementMode`、`ScreenShotComparisonTools`、`ToolMenus`、`AssetTools` 等。

## 维护状态

### 近期更新

| 日期 | Commit | 内容 |
|---|---|---|
| 2024-11-09 | `66e9bb39ff7e` | 移除 5.2 时代的 `#if UE_ENABLE_INCLUDE_ORDER_DEPRECATED` 宏包裹，纯代码清理 |
| 2024-10-22 | `cdf71bcfc40b` | 将容易混淆的 `IsNonPIEEditorOnly` 函数重命名为 `IsEditorOnlyLoadedInPIE`，提高可读性 |
| 2024-09-13 | `7de8b5dbba85` | 使 EditorFunctionalTest Actor 实例在 PIE（Play In Editor）中可见可用 |

### 维护评价

- **年龄**：创建于 2016 年，已超过 9 年，属于老牌插件
- **最近更新**：2024 年有 3 次更新，内容为代码清理和 API 重命名，非功能性变更
- **活跃度**：维护不活跃，代码量极小（仅 7 个源文件），功能稳定
- **状态**：默认未启用（`EnabledByDefault: false`），但不是实验性（`IsBetaVersion: false`）
- **推荐**：如果你需要编写 Editor-only 的功能测试或截图基准测试，这是必需的插件。代码量小、逻辑简单、风险极低。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/FunctionalTestingEditor)
- [FunctionalTesting 插件（运行时）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/FunctionalTesting)
