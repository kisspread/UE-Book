# Editor TRS Gizmo

> A temporary plugin for New TRS Gizmo work（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `EditorTRSGizmo` (Runtime), `EditorTRSGizmoSettings` (Runtime), `EditorTRSGizmoTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-19 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorTRSGizmo) | |

## 用途

这是一个用于 UE5.8 新版变换操控器（TRS Gizmo）开发的**临时实验性插件**。TRS 即 Translate（平移）、Rotate（旋转）、Scale（缩放）三大变换操作的缩写。

该插件存在的目的是为编辑器视口中变换操控器的重构工作提供一个独立的开发和测试环境。传统的变换 Gizmo 代码深度耦合在引擎核心中，将其提取为独立插件可以：

- 隔离新 Gizmo 的开发，避免影响现有编辑器功能
- 通过独立的测试模块（EditorTRSGizmoTests）快速验证新 Gizmo 的行为
- 便于在合入主分支前进行迭代实验

插件包含三个模块：核心 Gizmo 逻辑（EditorTRSGizmo）、用户设置（EditorTRSGizmoSettings）和自动化测试（EditorTRSGizmoTests），结构清晰，体现了从功能到配置到测试的完整开发流程。

> ⚠️ **注意**：这是一个临时插件，Description 明确标注为 "temporary"。最终新 Gizmo 代码可能会合入引擎核心后移除此插件。

## 使用场景

- 你正在参与 UE5.8 编辑器 Gizmo 重构工作 → 启用此插件测试新版变换操控器
- 你需要验证新 Gizmo 在不同变换模式下的行为是否正确 → 使用 EditorTRSGizmoTests 模块
- 你需要自定义 Gizmo 的外观或交互设置 → 通过 EditorTRSGizmoSettings 模块配置

## 蓝图用法

由于该插件主要面向编辑器 Gizmo 底层实现，且为实验性临时插件，蓝图暴露的接口有限。核心交互通过编辑器视口直接完成，而非蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （待源码确认） | 该插件的 API 主要面向 C++ 层 | — |

> 该插件为编辑器底层 Gizmo 实现，主要通过 C++ 扩展而非蓝图节点使用。

## C++ 用法

### 头文件引入

```cpp
#include "EditorTRSGizmo.h"
```

### 基本用法

由于该插件为实验性临时插件，具体 API 需参考源码。以下为典型使用模式：

```cpp
// 引入 Gizmo 核心模块
#include "EditorTRSGizmo.h"

// 引入 Gizmo 设置模块
#include "EditorTRSGizmoSettings.h"
```

### 进阶用法

该插件的测试模块（EditorTRSGizmoTests）提供了自动化测试用例，可作为理解 Gizmo 行为的参考。测试用例通常采用 UE 自动化测试框架：

```cpp
// 测试 Gizmo 变换行为的典型模式
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FEditorTRSGizmoTest,
    "Editor.TRSGizmo.BasicTransform",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter
)

bool FEditorTRSGizmoTest::RunTest(const FString& Parameters)
{
    // 测试平移、旋转、缩放 Gizmo 的基本行为
    // 具体实现参见 EditorTRSGizmoTests 模块源码
    return true;
}
```

## Demo 示例

```cpp
// MyGizmoTest.h
#pragma once

#include "CoreMinimal.h"

class FMyGizmoTest
{
public:
    /** 初始化 Gizmo 测试环境 */
    void Initialize();

    /** 验证变换操作 */
    void TestTransform();
};
```

```cpp
// MyGizmoTest.cpp
#include "MyGizmoTest.h"
#include "EditorTRSGizmo.h"

void FMyGizmoTest::Initialize()
{
    // 初始化测试环境
    // 具体 API 参见 EditorTRSGizmo 模块
}

void FMyGizmoTest::TestTransform()
{
    // 测试平移、旋转、缩放操作
}
```

> ⚠️ 由于该插件为实验性临时插件，API 可能随版本快速变化。建议直接阅读源码获取最新接口。

## 模块依赖

从 Build.cs 分析，该插件的模块依赖如下：

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | 该插件作为编辑器 Gizmo 实现，主要依赖引擎核心模块 |

> 三个模块（EditorTRSGizmo、EditorTRSGizmoSettings、EditorTRSGizmoTests）之间存在内部依赖关系：Tests 模块依赖核心模块和设置模块。

## 维护状态

### 近期更新

- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-03-23 `4803c798` [Editor TRS] Move from EditorTRSGizmo -> EditorInteractiveToolsFramework
- 2026-03-20 `befbf13e` [Gizmos] Add RowTags to gizmo settings customization so they have unique names
- 2026-03-20 `65f0592e` [ITF Gizmos] Gizmo and Duplicate actions trigger when piloting an Actor and using LMB + Alt
- 2026-03-19 `ce9d9a8c` [Viewport ITF] Condense the OnTerminateDragSequence() and OnForceEndCapture() functions (neither of 

> 由于该插件创建时间较近（2026-03-19），git log 中暂无后续更新记录。

### 维护评价

- **创建时间**：2026-03-19，非常新的插件
- **维护状态**：🆕 新创建，处于活跃开发初期
- **实验性标记**：IsExperimentalVersion = true，明确标注为实验性
- **临时性质**：Description 明确标注为 "temporary"，预计在 Gizmo 重构完成后会被移除或合并
- **推荐使用**：⚠️ **仅推荐参与 Gizmo 重构的开发者使用**。普通用户不应依赖此插件，因为：
  1. 它是临时性的，可能随时被移除
  2. API 不稳定，可能随版本快速变化
  3. 最终功能会合入引擎核心

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorTRSGizmo)
- 官方文档：无（实验性临时插件，暂无官方文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorTRSGizmo/Source/EditorTRSGizmoTests)