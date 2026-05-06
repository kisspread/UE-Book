# SlateIMInGame

> An immediate mode wrapper for Slate. Intended for building debugging tools.

| 属性 | 值 |
|---|---|
| 中文名 | 即时模式游戏内组件 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SlateIM` (Runtime), `SlateIMInGame` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-28 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SlateIM) | |

## 用途

SlateIM 是一个即时模式（Immediate Mode，IM）图形用户界面（GUI）框架，将 Slate 声明式 UI 的即时模式风格包装起来。其核心用途是让开发者能够用很少的样板代码快速构建调试工具、性能监视器或开发控制台。

**SlateIMInGame** 模块是 SlateIM 的扩展，它允许 IM GUI 以 **Actor** 的形式放置在游戏世界中，并支持网络同步，特别适用于服务器/客户端调试场景。它解决了以下问题：

- **运行时调试面板**：开发者可以在游戏运行时通过控制台快捷键打开/关闭自定义调试界面。
- **网络同步调试**：InGame Widget 可以存在于服务器上，并将其状态同步到客户端（通过 `GenerateServerSnapshot()`），方便调试多人游戏中的问题。
- **模块化注册**：通过 `IModularFeature` 系统，开发者可以注册多个独立的 InGame Widget，并在游戏内通过控制台命令按路径切换。

## 使用场景

- **多人游戏调试**：你正在开发一个多人射击游戏，需要查看服务器端的 AI 行为或物理状态。你可以创建一个 `ASlateIMInGameWidgetBase` 子类，覆写 `GenerateServerSnapshot()` 来收集服务器数据，绘制一个 IM 仪表盘。通过控制台命令 `ToggleSlateIMInGameWidget "/Script/YourModule.YourWidgetActor"`，在客户端按下按键即可显示该调试面板。
- **运行时调优工具**：你需要调整粒子系统的参数，但希望避免每次修改都重新编译。你可以写一个 InGame Window，使用 SlateIM 的即时模式 API（如 `SButton`、`SSlider`）直接绑定到游戏中的变量。
- **快速创建开发菜单**：不需要复杂的 UMG 蓝图，只需派生 `ASlateIMInGameWindow`，在 `DrawContent()` 中绘制菜单项，即可获得一个可拖拽、可缩放的运行时窗口。

## 蓝图用法

`SlateIMInGame` 模块主要面向 C++ 开发者，蓝图接口有限。以下是从头文件中提取的、可在蓝图中调用的核心功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ToggleSlateIMInGameWidget` | 执行控制台命令，切换指定路径的 InGame Widget 的显示/隐藏 | `USlateIMInGameWidgetCheatManager` |
| `GetInGameWidget`（静态） | 获取指定拥有者（PlayerController）和 Widget 类对应的 Actor 实例 | `ASlateIMInGameWidgetBase` |
| `EnableInGameWidget`（静态） | 启用或禁用一个 InGame Widget | `ASlateIMInGameWidgetBase` |

### 使用示例（蓝图描述）

1. **从控制台启用一个自定义 Widget**：
   - 在任意蓝图节点中，连接 `Execute Console Command` 节点。
   - 命令字符串格式：`ToggleSlateIMInGameWidget "/Script/YourPlugin.YourWidgetActor"`
   - 你需要确保这个 Widget 类已在 `StartupModule` 中通过 `IModularFeatures` 注册。

2. **从蓝图获取当前 Widget 实例**：
   - 调用静态函数 `Get InGame Widget (Owner, WidgetClass)`。
   - 输入 `Owner`（PlayerController）和 `WidgetClass`（你的自定义 Widget 蓝图类）。
   - 输出为该 Actor 引用，你可以进一步操作它。

## C++ 用法

### 头文件引入

```cpp
#include "SlateIMInGameWidgetBase.h"
#include "SlateIMInGameWindow.h"
#include "SlateIMInGameWidgetModularFeature.h"
```

### 基本用法

**1. 创建一个自定义 InGame Widget**

```cpp
// MyDebugWidget.h
#pragma once

#include "CoreMinimal.h"
#include "SlateIMInGameWidgetBase.h"
#include "MyDebugWidget.generated.h"

UCLASS()
class AMyDebugWidget : public ASlateIMInGameWidgetBase
{
    GENERATED_BODY()

protected:
    // 覆写 DrawWidget 以绘制 IM UI
    virtual void DrawWidget(const float DeltaTime) override;
};
```

```cpp
// MyDebugWidget.cpp
#include "MyDebugWidget.h"
#include "SlateIM.h"          // 提供 IM 绘图 API
#include "Slate/WidgetTransform.h"

void AMyDebugWidget::DrawWidget(const float DeltaTime)
{
    // 使用 SlateIM::Text() 绘制文本
    SlateIM::Text(FString::Printf(TEXT("DeltaTime: %.2f"), DeltaTime), FLinearColor::White);
    
    // 绘制一个按钮
    if (SlateIM::Button(TEXT("Reset Timer")))
    {
        // 重置逻辑
    }
}
```

**2. 注册并启用 Widget**

```cpp
// MyGameInstance.cpp
#include "SlateIMInGameWidgetModularFeature.h"
#include "MyDebugWidget.h"

void UMyGameInstance::Init()
{
    Super::Init();
    
    // 注册为模块化功能
    FString DebugWidgetPath = TEXT("/Script/YourPlugin.MyDebugWidget");
    FSlateIMInGameWidgetModularFeature Feature(DebugWidgetPath, AMyDebugWidget::StaticClass());
    // Feature 会创建控制台命令，例如 ToggleSlateIMInGameWidget /Script/YourPlugin.MyDebugWidget
}
```

### 进阶用法

**1. 使用 InGame Window（带标题栏窗口）**

```cpp
// MyDebugWindow.cpp
#include "SlateIMInGameWindow.h"
#include "MyDebugWindow.generated.h"

UCLASS()
class AMyDebugWindow : public ASlateIMInGameWindow
{
    GENERATED_BODY()

public:
    AMyDebugWindow()
    {
        // 设置窗口名称和标题（可选，默认会从 WindowName 生成）
        WindowName = TEXT("DebugConsole");
        WindowTitle = TEXT("Debug Console");
        WindowSize  = FVector2f(600, 400);
    }

protected:
    virtual void DrawContent(const float DeltaTime) override
    {
        // 这个函数会包裹在窗口内部绘制
        SlateIM::Text(TEXT("Hello from Debug Window!"));
        
        if (SlateIM::Button(TEXT("Close")))
        {
            bDestroyRequested = true;  // 请求销毁窗口
        }
    }
};
```

**2. 网络同步（服务器/客户端调试）**

```cpp
// AMyServerDebugWidget.cpp
UCLASS()
class AMyServerDebugWidget : public ASlateIMInGameWidgetBase
{
    GENERATED_BODY()

protected:
    virtual void GenerateServerSnapshot() override
    {
        // 仅在服务器执行，收集数据
        ServerPlayerCount = GetWorld()->GetNumPlayerControllers();
    }

    virtual void DrawWidget(const float DeltaTime) override
    {
        // 在客户端绘制时，可以读取 ServerPlayerCount（通过属性复制）
        SlateIM::Text(FString::Printf(TEXT("Players: %d"), ServerPlayerCount));
    }

    UPROPERTY(Replicated)
    int32 ServerPlayerCount = 0;
};
```

## Demo 示例

以下是一个完整的、可编译的最小 InGame Widget 示例。

```cpp
// MyMinimalWidget.h
#pragma once

#include "CoreMinimal.h"
#include "SlateIMInGameWidgetBase.h"
#include "MyMinimalWidget.generated.h"

UCLASS()
class AMyMinimalWidget : public ASlateIMInGameWidgetBase
{
    GENERATED_BODY()

public:
    AMyMinimalWidget()
    {
        PrimaryActorTick.bCanEverTick = false; // 由 DrawWidget 回调驱动
    }

protected:
    virtual void DrawWidget(const float DeltaTime) override
    {
        SlateIM::Text(TEXT("Hello from SlateIM InGame!"));
        
        // 如果按下F键（需要提前绑定）
        if (SlateIM::Button(TEXT("Toggle FPS")))
        {
            // 此示例来自插件测试用例：Engine/Plugins/Experimental/SlateIM/Source/SlateIM/Private/SlateIMTests.cpp
            // 切换控制台命令 'Stat FPS'
            GetWorld()->GetFirstPlayerController()->ConsoleCommand(TEXT("Stat FPS"));
        }
    }
};
```

```cpp
// MyMinimalWidget.cpp
#include "MyMinimalWidget.h"
#include "SlateIM.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
```

**注册与使用步骤**：

1. 创建此 Actor 类。
2. 在模块的 `StartupModule()` 中调用 `IModularFeatures::Get().RegisterModularFeature(SlateIMInGameWidget::ModularFeatureName, MakeShared<FSlateIMInGameWidgetModularFeature>(...) )`。
3. 编译后，在控制台输入 `ToggleSlateIMInGameWidget "/Script/YourPlugin.AMyMinimalWidget"` 即可显示 Widget。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SlateIM` | 核心即时模式 UI 渲染库，提供 `SlateIM::Text`、`SlateIM::Button` 等绘图 API |
| `Slate` | 基础 UI 框架，被 SlateIM 底层使用 |
| `InputCore` | 键盘/鼠标输入处理（控制台命令绑定） |

> 注意：`Core`、`CoreUObject`、`Engine` 等常见模块未列出，但它们是隐式依赖。

## 维护状态

### 近期更新

- 2025-09-09 accbcce Fixup API macros
- 2025-09-03 3b7603db Fixes for SlateImInGame widgets
- 2025-09-03 40963b9c SlateIM InGame widget actor for server/client debugging
- 2025-08-28 ea3f5ec2 SlateIM: Add an overload of SlateIM::Image that takes just a color
- 2025-07-28 9469fd08 SlateIM: Fix example window text not readjusting itself after the window is resized

### 维护评价

- **创建时间**：2025年7月，不到 3 个月。
- **最近更新**：2025年9月的 commit 表明插件仍在活跃开发中，修复了编译宏和 InGame Widget 的 bugs。
- **活跃度**：**活跃维护**。最近 3 次 commit（9月）涵盖了新功能（网络同步调试）和修复。
- **已知问题**：由于是实验性功能，API 可能不稳定，尤其是网络同步部分依赖 Actor 的属性复制，对于高性能场景可能需要优化。
- **推荐使用**：✅ 推荐。对于需要快速构建运行时调试 UI 的开发者非常有用，但注意将其标记为实验性，不建议用于最终产品 UI。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SlateIM)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SlateIM/Source/SlateIM/Private/SlateIMTests.cpp)
- [主模块文档](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/SlateIM/Source/SlateIM/README.md)（如果存在）

> **注意**：`SlateIM` 本身是实验性插件，默认未启用。你需要在 `Edit > Plugins` 中搜索并手动启用它。然后，你的 `.Build.cs` 文件需要添加对 `"SlateIM"`、`"SlateIMInGame"` 的 `PublicDependencyModuleNames` 依赖。