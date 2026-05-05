# Automation Utilities

> Tools and Utilities for Automation purposes

| 属性 | 值 |
|---|---|
| 分类 | Testing |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | AutomationUtils (Runtime), AutomationUtilsEditor (Editor) |
| 创建时间 | 2019-03-26 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AutomationUtils) | |

## 用途

AutomationUtils 提供**自动化截图测试**的核心能力。它解决的问题是：在 CI/CD 流水线中自动捕获游戏画面截图，并将其与基准图像（Ground Truth）进行像素级比较，从而检测渲染回归。

整个流程分两步：
1. **截图捕获**（Runtime 模块）：在游戏运行时截图，同时记录 RHI、GPU 驱动、画质设置等元数据，确保比较在相同硬件/配置下进行
2. **截图比较**（Editor 模块）：通过 Commandlet 批量比较 Incoming 截图与基准截图，输出 New/Pass/Fail 结果

这是一个面向 CI 和自动化测试管线的工具，不是给玩家或普通设计师用的。

## 使用场景

- 你在 CI 流水线中运行游戏自动化测试，需要捕获截图并检测渲染回归 → 用 AutomationUtils
- 你需要在不同硬件/平台上自动截取游戏画面，附带完整环境元数据 → 用 `TakeGameplayAutomationScreenshot`
- 你需要批量比较新截图与已批准的基准截图 → 用 `ScreenshotComparisonCommandlet`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Take Gameplay Automation Screenshot` | 捕获当前游戏画面截图，自动刷新加载流、编译 shader、stream in 纹理后截图，并附带完整的渲染元数据 JSON | `UAutomationUtilsBlueprintLibrary` |

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| ScreenshotName | String | — | 截图名称，用于文件名和标识 |
| MaxGlobalError | Float | 0.02 | 全局最大允许误差（比较时用） |
| MaxLocalError | Float | 0.12 | 局部最大允许误差（比较时用） |
| MapNameOverride | String | 空 | 覆盖地图名称（默认用当前关卡名） |

### 使用示例（蓝图描述）

在自动化测试蓝图中：
1. 使用 `Load Level` 节点加载目标关卡
2. 使用 `Delay` 等待关卡完全加载
3. 连接 `Take Gameplay Automation Screenshot` 节点，填入截图名称如 `"MyTest_Screenshot01"`
4. 调整 MaxGlobalError / MaxLocalError 控制比较容差（默认值适合大多数情况）

## C++ 用法

### 头文件引入

```cpp
#include "AutomationUtilsBlueprintLibrary.h"
```

### 基本用法

```cpp
// 截取当前游戏画面，使用默认容差
UAutomationUtilsBlueprintLibrary::TakeGameplayAutomationScreenshot(
    TEXT("TestScreenshot_01")
);
```

### 进阶用法

```cpp
// 自定义容差和地图名称
// MaxGlobalError=0.05 允许更大的全局差异
// MaxLocalError=0.20 允许更大的局部差异
// MapNameOverride 用于覆盖元数据中的地图名
UAutomationUtilsBlueprintLibrary::TakeGameplayAutomationScreenshot(
    TEXT("CombatScene_HighDetail"),
    0.05f,   // MaxGlobalError
    0.20f,   // MaxLocalError
    TEXT("GameplayMap")  // MapNameOverride
);
```

截图流程内部会自动执行以下操作：
1. `FlushAsyncLoading` — 等待异步加载完成
2. `FlushLevelStreaming` — 完成关卡流式加载
3. `SubmitRemainingJobsForWorld` — 提交材质编译任务（非 Cooked 数据）
4. `FAssetCompilingManager::FinishAllCompilation` — 完成所有资产编译
5. `StreamAllResources` — 强制加载所有资源
6. `ForceUpdateTextureStreaming` — 强制加载所有 MipMap
7. 注册 `FAutomationUtilsGameplayViewExtension` 临时关闭抗锯齿、运动模糊、AO 等噪声源
8. 截图保存为 PNG + JSON 元数据

## Demo 示例

### 最小自动化测试示例

```cpp
// MyScreenshotTest.h
#pragma once

#include "Misc/AutomationTest.h"

// .h + .cpp + Build.cs 中添加 "AutomationUtils" 模块依赖
```

```cpp
// MyScreenshotTest.cpp
#include "Misc/AutomationTest.h"
#include "AutomationUtilsBlueprintLibrary.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FMyScreenshotTest,
    "Project.Screenshots.CombatScene",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter
)

bool FMyScreenshotTest::RunTest(const FString& Parameters)
{
    // 加载关卡后截图（实际使用中需要先加载关卡并等待就绪）
    UAutomationUtilsBlueprintLibrary::TakeGameplayAutomationScreenshot(
        TEXT("CombatScene_Default"),
        0.02f,
        0.12f
    );
    return true;
}
```

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "AutomationUtils"
});
```

### ScreenshotComparisonCommandlet 用法

Commandlet 在 Editor 模块中，通过命令行调用：

```bash
# 比较所有 Incoming 截图
UnrealEditor-Cmd.exe ProjectName -run=ScreenshotComparison

# 只比较指定地图的截图
UnrealEditor-Cmd.exe ProjectName -run=ScreenshotComparison -Maps=MapA+MapB
```

输入路径：`{AutomationDir}/Incoming/`
基准路径：`{ProjectDir}/Test/Screenshots/`

## 模块依赖

### AutomationUtils (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（GameViewport、World 等） |
| `Json` | 元数据 JSON 序列化（私有） |
| `RHI` | 硬件信息查询（私有） |
| `RenderCore` | 渲染命令、SceneViewExtension（私有） |

### AutomationUtilsEditor (Editor)

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `Json` | JSON 解析 |
| `JsonUtilities` | JSON 与 UStruct 互转 |
| `AutomationMessages` | 自动化消息定义 |
| `ScreenShotComparisonTools` | 截图比较核心工具 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-04-23 | `89df8c170d23` | 将所有方法/静态变量的 dllexport 改为基于类型的导出 | 基础设施重构，非功能性变更 |
| 2024-11-25 | `af0eb101af7c` | 移除场景扩展方法的纯虚函数要求 | 跟随引擎 SceneViewExtension 接口变更 |
| 2024-11-09 | `66e9bb39ff7e` | 移除 UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 宏 | 代码清理，非功能性变更 |

### 维护评价

- **创建时间**：2019 年，已有 7 年历史
- **近期更新**：最近 3 次 commit 均为引擎级别的基础设施适配（dllexport 风格变更、接口纯虚函数移除、宏清理），没有功能性更新
- **维护状态**：处于 **被动维护** 状态 — 跟随引擎编译/API 变更而调整，但核心功能未见演进
- **Beta 标记**：`.uplugin` 中 `IsBetaVersion: true`，表明 Epic 从未将其标记为正式版
- **文件规模**：仅 6 个源文件，功能非常集中
- **已知限制**：截图比较依赖 `ScreenShotComparisonTools` 模块；元数据中的 DeviceId 在某些平台可能为空（代码中已处理 fallback）
- **是否推荐使用**：如果你需要在 CI 中做截图回归测试，这个 plugin 提供了基础能力且默认启用。但要注意它仍标记为 Beta，功能较为基础，复杂需求可能需要自行扩展。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AutomationUtils)
- 官方文档（无）
