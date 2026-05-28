# Automation Utilities

> Tools and Utilities for Automation purposes

| 属性 | 值 |
|---|---|
| 中文名 | 自动化工具箱 |
| 分类 | Testing |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AutomationUtils` (Runtime), `AutomationUtilsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-03-26 |
| 年龄标签 | 🐺 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AutomationUtils) | |

## 用途

提供在游戏运行时或编辑器中执行自动化截图（Automation Screenshot）以及进行离线图片对比的工具。它解决了需要在没有自动化测试框架（FTest）运行的情况下，在游戏进程中直接捕获截图，以及后续批量进行图像差异分析的问题。是自动化测试流程中的一个实用工具集。

## 使用场景

- 你需要在游戏玩法中捕获特定画面用于自动化视觉回归测试，但不想启动完整的自动化测试流程。
- 你需要在不同的目标平台（如不同主机）上采集截图，然后在一台机器上批量、离线地进行图像对比，以检查渲染差异。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AutomationScreenshot` | 在游戏世界中拍摄一张用于自动化比较的截图。 | `UAutomationUtilsBlueprintFunctionLibrary` |

### 使用示例（蓝图描述）

在事件图表中，调用 `AutomationScreenshot` 节点。通常将此调用连接到一个输入事件（如按键）或某个游戏逻辑完成后，即可在运行时捕获当前画面的截图。

## C++ 用法

### 头文件引入

```cpp
#include "AutomationUtilsBlueprintFunctionLibrary.h"
```

### 基本用法

使用蓝图函数库中的静态方法直接拍摄截图。
```cpp
// 假设在一个Actor或Component的某个函数内
#include "AutomationUtilsBlueprintFunctionLibrary.h"

void AMyTestActor::CaptureCurrentView()
{
    // 调用蓝图函数库中的截图函数
    UAutomationUtilsBlueprintFunctionLibrary::AutomationScreenshot(GetWorld());
}
```
*（来源：基于 `UAutomationUtilsBlueprintFunctionLibrary` 的公开API推断）*

### 进阶用法

可以结合定时器或特定的游戏状态判断，在多个时间点或位置自动触发截图，为后续的批量对比收集素材。

## Demo 示例

以下是一个最小化的 Actor 示例，用于在 BeginPlay 时拍摄一张自动化截图。

**头文件 (AMyAutomationTestActor.h):**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyAutomationTestActor.generated.h"

UCLASS()
class AMyAutomationTestActor : public AActor
{
    GENERATED_BODY()
    
public:
    virtual void BeginPlay() override;
};
```

**源文件 (AMyAutomationTestActor.cpp):**
```cpp
#include "MyAutomationTestActor.h"
#include "AutomationUtilsBlueprintFunctionLibrary.h"

void AMyAutomationTestActor::BeginPlay()
{
    Super::BeginPlay();
    // 游戏开始后立即拍摄一张自动化截图
    UAutomationUtilsBlueprintFunctionLibrary::AutomationScreenshot(GetWorld());
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ImageCore` | 提供核心图像处理功能，用于截图和可能的图像操作。 |
| `AutomationTest` | 提供自动化测试的底层框架支持。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `ec6539e3` | Add FinishAllAssetCompilation to fix material instance test crash | 修复了材质实例测试崩溃的问题。 |
| 2026-05-12 | `52ac5ba2` | Add support for registering an automation mount point to the AutomationUtils BPFL. This allows thing | 为自动化工具箱添加了挂载点注册支持，扩展了功能。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到更现代的 UE_LOGF。 |

### 维护评价

该插件创建于2019年，标记为实验性。从最近的提交历史看，在2026年5月仍有活跃的功能性更新（如修复崩溃、增加新功能），表明它仍在被**积极维护**和使用。尽管标记为Beta，但其核心的截图与对比功能在自动化测试流程中具有实用价值。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AutomationUtils)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AutomationUtils/Tests) （如果存在，位于插件目录内的Tests文件夹）