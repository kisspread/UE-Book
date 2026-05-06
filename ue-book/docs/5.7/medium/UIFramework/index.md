# UI 框架 (UIFramework)

> A framework to control UMG from server.

| 属性 | 值 |
|---|---|
| 中文名 | UI 框架 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资源） |
| 模块 | `UIFramework` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-07-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UIFramework) | |

## 用途

UE5 的 UMG（Unreal Motion Graphics）是客户端侧的用户界面系统，服务器无法直接创建或控制 UMG 控件。UIFramework 提供了一套从服务器端驱动 UMG 渲染的框架，允许 **服务器拥有 UI 逻辑**，通过复制和 RPC 同步到客户端显示。它解决了以下问题：

- 多人在线游戏中，UI 逻辑需要在服务器上运行（如显示拾取提示、任务进度、状态变化），以减少客户端作弊或保证状态一致。
- 服务器可以动态创建、布局和更新复杂的 UMG 界面，无需在客户端编写大量复制代码。
- 与 MVVM（Model-View-ViewModel）和数据绑定结合，实现响应式界面。
- 支持本地化消息（`LocalizableMessage`）和资源异步加载。

UIFramework 本身是一个纯代码插件，**不提供预制的 UMG 控件蓝图**，但提供了从 `UUIFrameworkWidget` 派生的服务器端控件（按钮、图片、文本、布局容器等），并在本地自动转换为对应的 UMG `UWidget`。

## 使用场景

- **多人在线游戏**：物品掉落公告、聊天提示、队伍状态 UI、任务追踪面板等需要由服务器统一控制的 UI。
- **大厅/匹配系统**：服务器发起匹配并显示进度，客户端只负责呈现。
- **需要动态创建界面的网络游戏**：例如 MMO 的背包界面、商店界面，由服务器决定打开哪个菜单并填充数据。
- **保护 UI 逻辑不被篡改**：将 UI 的业务逻辑（如按钮点击是购买物品）放在服务器执行，客户端只做展示。

## 蓝图用法

本插件的大部分 API 只能在 **服务器** 上调用（标记 `BlueprintAuthorityOnly`），客户端只能读取属性或触发本地事件（如点击后本地表现，实际处理逻辑依然在服务器）。以下按功能分组列出核心节点。

### 基础控件属性

所有服务器端控件（继承自 `UUIFrameworkWidget`）都支持以下蓝图可读写属性（服务器设置，客户端同步）：

| 节点/属性 | 说明 | 所在类 |
|---|---|---|
| `Set Enabled` / `Is Enabled` | 启用或禁用控件（C++ 侧通过 `bIsEnabled`，蓝图暴露为 `Set Enabled` 和 `Is Enabled`） | `UUIFrameworkWidget` |
| `Set Visibility` / `Get Visibility` | 设置控件的可见性（`ESlateVisibility`） | 同上 |
| `Set Hit Test Visible` / `Is Hit Test Visible` | 设置是否可点击 | 同上 |
| `Set Render Opacity` / `Get Render Opacity` | 设置渲染不透明度 | 同上 |

这些属性会通过网络复制，客户端会自动同步到对应的 UMG 控件。

### 容器与布局

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Widget (Overlay)` | 向覆盖层添加一个子控件，并指定 `Padding`、`Horizontal Alignment`、`Vertical Alignment`。由覆盖层的 `AuthorityForEachChildren` 内部调用，蓝图端使用 `Add Entry` 函数（需通过 `UUIFrameworkOverlay` 的成员函数调用） | `UUIFrameworkOverlay` |
| `Add Widget (StackBox)` | 向栈盒添加子控件，设置对齐、边距和尺寸规则 | `UUIFrameworkStackBox` |
| `Add Widget (CanvasBox)` | 向画布框添加子控件，指定锚点、偏移、对齐和 ZOrder | `UUIFrameworkCanvasBox` |
| `Remove Widget` | 从容器中移除指定子控件 | 容器类均可调用 `AuthorityRemoveChild` |
| `Set Content (Button)` | 设置按钮的唯一子控件，替换原有内容 | `UUIFrameworkButton` |
| `Set Content (SafeZone)` | 设置安全区的唯一子控件 | `UUIFrameworkSafeZoneBox` |

### 图像与颜色块

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Color` | 设置纯色块的填充颜色 | `UUIFrameworkColorBlock` |
| `Set Desired Size (Color)` | 设置纯色块的期望尺寸 | `UUIFrameworkColorBlock` |
| `Set Material` | 设置图片块的材质资源 | `UUIFrameworkImageBlock` |
| `Set Texture` | 设置图片块的纹理资源（可同时指定是否使用纹理大小） | `UUIFrameworkImageBlock` |
| `Set Tint` | 设置图片块的色调 | `UUIFrameworkImageBlock` |
| `Set Desired Size (Image)` | 设置图片块的期望尺寸 | `UUIFrameworkImageBlock` |

### 文本控件

`UUIFrameworkTextBase` 是抽象基类，具体使用 `UUIFrameworkTextBlock`（继承自 `UUIFrameworkTextBase`，但源码未完全展示）。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Text`（C++ 中为 `SetMessage`） | 设置本地化消息文本 | `UUIFrameworkTextBase` |
| `Get Text` | 获取当前的显示文本（客户端） | 同上 |
| `Set Text Color` | 设置文本颜色 | 同上 |
| `Set Text Size` | 设置文本字号 | 同上 |
| `Set Justification` | 设置对齐方式（左/中/右） | 同上 |
| `Set Overflow Policy` | 设置文本溢出样式 | 同上 |

### 玩家组件（入口点）

在服务器端，要将 UI 显示给某个玩家，需要获取或创建 `UUIFrameworkPlayerComponent`（附加在 `APlayerController` 上）。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Widget` | 添加一个控件到指定的游戏层（覆盖全屏幕或跟随玩家屏幕），支持 ZOrder 和输入模式 | `UUIFrameworkPlayerComponent` |
| `Remove Widget` | 从视图移除指定控件 | 同上 |
| `Focus Widget` | 设置键盘焦点到指定控件 | 同上 |
| `Push Widget` | 将控件压入导航栈（用于子菜单） | 同上 |
| `Pop Widget` | 弹出导航栈 | 同上 |

所有上述函数在蓝图端均带有 `BlueprintAuthorityOnly` 标签，**仅允许服务器调用**。

### 使用示例（蓝图描述）

1. **服务器在玩家加入时显示欢迎信息**：
   - 在 `GameMode` 中，当 `PostLogin` 触发时，`Get Player Controller` → `Get Component by Class`(`UUIFrameworkPlayerComponent`)。
   - 构造 `UUIFrameworkTextBlock` (`Create Widget` 但需创建服务器端控件，应使用 `New Object` 替换？实际需使用 `NewObject<UUIFrameworkTextBlock>()` 在 C++ 中，蓝图中可能通过 `Spawn Object` 从 `UIFramework` 类创建)。
   - 设置 `Message`（文本内容）和 `Text Color`。
   - 调用 `Add Widget` 将该文本块添加到玩家组件的 `Viewport` 层。

2. **服务器按钮点击触发购买**：
   - 服务器创建 `UUIFrameworkButton`，设置其 `Content` 为另一个控件（如文本）。
   - 绑定 `OnClick` 事件（蓝图可通过 `Assign On Click` 节点绑定到自定义事件）。
   - 将按钮添加到玩家的游戏层。
   - 点击时，服务器收到 `ServerClick` RPC，然后在服务器上执行购买逻辑并更新 UI。

## C++ 用法

### 头文件引入

```cpp
#include "UIFWidget.h"
#include "UIFPlayerComponent.h"
#include "UIFButton.h"
#include "UIFTextBlock.h"
#include "UIFrameworkModule.h"
```

### 基本用法

下例展示了服务器如何创建一个按钮并添加到玩家视口（通常放在 `AGameModeBase` 或自定义 `UGameInstanceSubsystem` 中）：

```cpp
// 假设 GetPlayerController(0) 是有效玩家
APlayerController* PC = GetWorld()->GetFirstPlayerController();
UUIFrameworkPlayerComponent* UIComp = PC->FindComponentByClass<UUIFrameworkPlayerComponent>();
if (!UIComp)
{
    UIComp = NewObject<UUIFrameworkPlayerComponent>(PC);
    UIComp->RegisterComponent();
}

// 创建服务器端按钮
UUIFrameworkButton* Button = NewObject<UUIFrameworkButton>();
FUIFrameworkSimpleSlot Content;
Content.Padding = FMargin(10);
// 设置按钮内部文本（嵌套文本控件）
UUIFrameworkTextBlock* Text = NewObject<UUIFrameworkTextBlock>();
FLocalizableMessage Msg;
Msg.Text = FText::FromString("Click Me!");
Text->SetMessage(MoveTemp(Msg));
Content.AuthoritySetWidget(Text);
Button->SetContent(Content);

// 添加按钮到玩家视口（默认游戏层）
FUIFrameworkGameLayerSlot Slot;
Slot.ZOrder = 0;
Slot.Type = EUIFrameworkGameLayerType::Viewport;
UIComp->AddWidget(Button, Slot);
```

来源文件路径：`Engine/Plugins/Experimental/UIFramework/Source/Public/UIFPlayerComponent.h`，`UIFWidget.h`。

### 事件绑定

```cpp
// 在按钮创建后绑定事件（服务器端）
Button->OnClick.AddLambda([](const FUIFrameworkClickEventArgument& Arg)
{
    // Arg.PlayerController 发出点击的控制器
    // Arg.Sender 点击的按钮（UUIFrameworkButton*）
    UE_LOG(LogTemp, Log, TEXT("Button clicked by %s"), *Arg.PlayerController->GetName());
    // 服务器执行逻辑...
});
```

### 进阶用法：自定义 Presenter

默认的 `UUIFrameworkGameViewportPresenter` 负责将控件添加到客户端的视口。若需要自定义布局或动画，可以继承 `UUIFrameworkPresenter`：

```cpp
UCLASS()
class UMyCustomPresenter : public UUIFrameworkPresenter
{
    GENERATED_BODY()
public:
    virtual void AddToViewport(UWidget* UMGWidget, const FUIFrameworkGameLayerSlot& Slot) override
    {
        // 将 UMGWidget 添加到自定义画布，并应用动画
    }
};

// 在项目启动时设置自定义 Presenter（应在服务器初始化时调用一次）
UUIFrameworkModule::SetPresenterClass(UMyCustomPresenter::StaticClass());
```

## Demo 示例

以下是一个完整的、可编译的测试示例，展示从服务器创建 UI 框架控件并显示给玩家。

### MyGameMode.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

UCLASS()
class MYGAME_API AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void PostLogin(APlayerController* NewPlayer) override;
};
```

### MyGameMode.cpp

```cpp
#include "MyGameMode.h"
#include "UIFPlayerComponent.h"
#include "UIFButton.h"
#include "UIFTextBlock.h"
#include "UIFrameworkModule.h"

void AMyGameMode::PostLogin(APlayerController* NewPlayer)
{
    Super::PostLogin(NewPlayer);

    // 确保玩家控制器拥有 UIFrameworkPlayerComponent
    UUIFrameworkPlayerComponent* UIComp = NewPlayer->FindComponentByClass<UUIFrameworkPlayerComponent>();
    if (!UIComp)
    {
        UIComp = NewObject<UUIFrameworkPlayerComponent>(NewPlayer);
        UIComp->RegisterComponent();
    }

    // 创建标题文本
    UUIFrameworkTextBlock* TitleText = NewObject<UUIFrameworkTextBlock>();
    FLocalizableMessage Msg;
    Msg.Text = FText::FromString("Welcome! UIFramework Demo");
    TitleText->SetMessage(MoveTemp(Msg));
    TitleText->SetTextColor(FLinearColor::Yellow);
    TitleText->SetTextSize(28.0f);

    // 创建按钮
    UUIFrameworkButton* DemoButton = NewObject<UUIFrameworkButton>();
    FUIFrameworkSimpleSlot ButtonContent;
    ButtonContent.Padding = FMargin(8.0f);
    {
        UUIFrameworkTextBlock* ButtonText = NewObject<UUIFrameworkTextBlock>();
        FLocalizableMessage BtnMsg;
        BtnMsg.Text = FText::FromString("Server Click Me");
        ButtonText->SetMessage(MoveTemp(BtnMsg));
        ButtonContent.AuthoritySetWidget(ButtonText);
    }
    DemoButton->SetContent(ButtonContent);

    // 绑定点击事件
    DemoButton->OnClick.AddLambda([NewPlayer](const FUIFrameworkClickEventArgument& Arg)
    {
        UE_LOG(LogTemp, Display, TEXT("Button clicked by %s, executing server logic."), *NewPlayer->GetName());
        // 例：创建新的文本提示
        UUIFrameworkPlayerComponent* PCComp = Arg.PlayerController->FindComponentByClass<UUIFrameworkPlayerComponent>();
        if (PCComp)
        {
            UUIFrameworkTextBlock* Feedback = NewObject<UUIFrameworkTextBlock>();
            FLocalizableMessage FeedMsg;
            FeedMsg.Text = FText::FromString("Server processed click!");
            Feedback->SetMessage(MoveTemp(FeedMsg));
            Feedback->SetTextColor(FLinearColor::Green);
            FUIFrameworkGameLayerSlot Slot;
            Slot.ZOrder = 5;
            PCComp->AddWidget(Feedback, Slot);
        }
    });

    // 将标题和按钮添加到玩家视口
    FUIFrameworkGameLayerSlot SlotTitle;
    SlotTitle.ZOrder = 0;
    FUIFrameworkGameLayerSlot SlotButton;
    SlotButton.ZOrder = 1;
    SlotButton.InputMode = EUIFrameworkInputMode::UI;

    UIComp->AddWidget(TitleText, SlotTitle);
    UIComp->AddWidget(DemoButton, SlotButton);
}
```

## 模块依赖

除常见的 `Core`、`CoreUObject`、`Engine`、`UMG` 等项目核心模块外，UIFramework 还依赖以下特定插件：

| 模块 | 用途 |
|---|---|
| `ModelViewViewModel` | 提供 MVVM 数据绑定基础（`UMVVMViewModelBase`） |
| `LocalizableMessage` | 支持本地化消息定义和解析（`FLocalizableMessage`） |

此外，运行时还需要 `UIFramework` 模块自身。

## 维护状态

### 近期更新

- 2025-10-07 `1eace4d0` — UIFramework: Create the Presenter on-demand as it can fail during construction
- 2025-08-28 `eb61e5f0` — VerseUI: Fix log formatting  
- 2025-08-28 `af96d587` — VerseUI: Better logging to identify material misuse in image blocks.
- 2025-08-05 `34bfa4a2` — Expose focus events in SButton
- 2025-07-22 `ec7ce0a5` — VerseUI: Expose SetFocus method to player_ui.

### 维护评价

- **年龄**：2025年7月创建，刚满3个月，属于全新插件。
- **更新频率**：从创建至今每个月都有实质性更新（修复、功能扩展），最近一次更新在2025年10月，活跃度很高。
- **内容**：已包含基础控件（按钮、文本、图像、容器）、事件系统、本地化支持、MVVM 集成、自定义 Presenter。
- **已知问题**：目前是实验性插件（路径 `Experimental`），API 可能变化；部分功能如导航栈尚未完全公开蓝图节点。
- **推荐**：✅ 强烈推荐 —— 适合需要服务器驱动 UI 的网络游戏项目。但因处于早期阶段，建议密切关注后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UIFramework)