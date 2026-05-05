# EditorTRSGizmo

> A temporary plugin for New TRS Gizmo work

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（Gizmo 资产，测试资源） |
| 模块 | `EditorTRSGizmo` (Runtime), `EditorTRSGizmoSettings` (Runtime), `EditorTRSGizmoTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-19 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorTRSGizmo) | |

## 用途

该插件是一个用于开发和测试新版变换 Gizmo（Translate/Rotate/Scale Gizmo）的临时性实验插件。它并非一个面向最终用户的稳定功能插件，而是 Epic Games 内部用于迭代和验证新 Gizmo 系统设计的工具。其核心目的是在不影响现有编辑器稳定性的前提下，隔离开发新的 Gizmo 交互逻辑、视觉表现和性能优化方案。

## 使用场景

- **引擎开发者/贡献者**：正在参与 Unreal Engine 编辑器 Gizmo 系统的重构或新功能开发，需要一个独立的沙盒环境进行测试。
- **需要深度定制编辑器工具的开发者**：希望研究或学习 Epic 官方如何实现复杂的 3D 操控手柄（Gizmo），并可能基于此开发自己的自定义 Gizmo。
- **自动化测试工程师**：需要验证 Gizmo 相关功能的正确性，该插件包含专门的测试模块。

## 蓝图用法

由于该插件主要面向引擎底层开发和测试，其公开的蓝图 API 非常有限。核心的 Gizmo 逻辑通常通过 C++ 与编辑器子系统交互。`EditorTRSGizmoSettings` 模块可能提供一些用于配置 Gizmo 行为的蓝图可调用设置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get EditorTRSGizmo Settings` | 获取编辑器 TRS Gizmo 的运行时设置对象 | `UEditorTRSGizmoSettings` |
| `Set Gizmo Scale` | 设置 Gizmo 在视口中的显示缩放比例 | `UEditorTRizmoSettings` |

### 使用示例（蓝图描述）

在编辑器工具蓝图（Editor Utility Blueprint）中，你可以通过 `Get EditorTRSGizmo Settings` 节点获取设置对象，然后读取或修改其属性（如 `bEnableNewGizmo`）来控制是否启用实验性 Gizmo。修改后可能需要调用相应的函数使设置生效。

## C++ 用法

该插件的 C++ 用法主要涉及访问和配置 Gizmo 设置，以及可能的 Gizmo 子系统交互。

### 头文件引入

```cpp
#include "EditorTRSGizmoSettings.h"
```

### 基本用法

访问 Gizmo 设置单例。
```cpp
// 获取 Gizmo 设置单例
UEditorTRSGizmoSettings* GizmoSettings = GetMutableDefault<UEditorTRSGizmoSettings>();
if (GizmoSettings)
{
    // 读取设置
    bool bIsNewGizmoEnabled = GizmoSettings->bEnableNewGizmo;
    
    // 修改设置（通常在编辑器偏好设置面板中操作）
    GizmoSettings->bEnableNewGizmo = true;
    GizmoSettings->PostEditChange(); // 通知设置已更改
}
```

### 进阶用法

结合编辑器子系统监听 Gizmo 状态变化。
```cpp
// 假设存在一个 Gizmo 子系统（需从源码确认）
// UEditorTRSGizmoSubsystem* GizmoSubsystem = GEditor->GetEditorSubsystem<UEditorTRSGizmoSubsystem>();
// if (GizmoSubsystem)
// {
//     // 订阅 Gizmo 模式切换事件
//     GizmoSubsystem->OnGizmoModeChanged.AddLambda([](EGizmoMode NewMode){
//         UE_LOG(LogTemp, Log, TEXT("Gizmo mode changed to: %d"), static_cast<int32>(NewMode));
//     });
// }
```

## Demo 示例

一个最小示例，演示如何在编辑器工具中检查并修改 Gizmo 设置。

**MyGizmoConfigTool.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "EditorUtilityWidget.h"
#include "MyGizmoConfigTool.generated.h"

class UEditorTRSGizmoSettings;

UCLASS()
class UMyGizmoConfigTool : public UEditorUtilityWidget
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Gizmo Config")
    void ToggleNewGizmo();

    UFUNCTION(BlueprintCallable, BlueprintPure, Category = "Gizmo Config")
    bool IsNewGizmoEnabled() const;

private:
    UPROPERTY()
    TWeakObjectPtr<UEditorTRSGizmoSettings> CachedSettings;
};
```

**MyGizmoConfigTool.cpp**
```cpp
#include "MyGizmoConfigTool.h"
#include "EditorTRSGizmoSettings.h"

void UMyGizmoConfigTool::ToggleNewGizmo()
{
    UEditorTRSGizmoSettings* Settings = GetMutableDefault<UEditorTRSGizmoSettings>();
    if (Settings)
    {
        Settings->bEnableNewGizmo = !Settings->bEnableNewGizmo;
        Settings->PostEditChange();
        CachedSettings = Settings;
    }
}

bool UMyGizmoConfigTool::IsNewGizmoEnabled() const
{
    const UEditorTRSGizmoSettings* Settings = GetDefault<UEditorTRSGizmoSettings>();
    return Settings ? Settings->bEnableNewGizmo : false;
}
```

## 模块依赖

从模块名称和常见实践推断，该插件可能依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `EditorTRSGizmo` | 提供核心的 Gizmo 实现和子系统 |
| `EditorTRSGizmoSettings` | 提供 Gizmo 相关的可配置设置 |
| `EditorFramework` | 提供编辑器框架和工具集支持 |
| `LevelEditor` | 与关卡编辑器视口交互 |

## 维护状态

### 近期更新

- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-03-23 `4803c798` [Editor TRS] Move from EditorTRSGizmo -> EditorInteractiveToolsFramework
- 2026-03-20 `befbf13e` [Gizmos] Add RowTags to gizmo settings customization so they have unique names
- 2026-03-20 `65f0592e` [ITF Gizmos] Gizmo and Duplicate actions trigger when piloting an Actor and using LMB + Alt
- 2026-03-19 `ce9d9a8c` [Viewport ITF] Condense the OnTerminateDragSequence() and OnForceEndCapture() functions (neither of 

### 维护评价

- **创建时间**：2026年3月，是一个非常新的插件。
- **维护频率**：作为实验性插件，其更新可能与引擎 Gizmo 系统的开发进度强相关，可能在特定版本周期内密集更新，之后可能被合并到主编辑器代码或废弃。
- **活跃状态**：标记为 `IsExperimentalVersion=true`，表明它正处于活跃的实验和开发阶段。
- **已知限制**：作为“临时”插件，其 API 和功能可能不稳定，随时可能发生破坏性更改或被移除。
- **推荐使用**：**不推荐**普通项目开发者将其作为稳定依赖。仅建议用于学习引擎内部实现、参与引擎开发，或在自己的实验性分支中进行 Gizmo 相关研究。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorTRSGizmo)
- [官方文档]() (无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorTRSGizmo/Source/EditorTRSGizmoTests)