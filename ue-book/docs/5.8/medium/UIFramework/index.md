# UIFramework

> A framework to control UMG from server.

| 属性 | 值 |
|---|---|
| 中文名 | 服务端UI框架 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UIFramework` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-07-18 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UIFramework) | |

## 用途

UIFramework 是一个**服务端权威**（Server-Authoritative）的 UMG UI 框架。它解决的核心问题是：在多人游戏中，UI 的状态和行为需要由服务器控制并复制到客户端，而不是每个客户端各自管理自己的 UI。

传统 UMG 的问题在于 UI 状态完全是本地的，服务端无法控制客户端显示什么界面、按钮是否可点击、文本内容是什么。UIFramework 通过以下方式解决这个问题：

1. **服务端创建和管理 Widget**：所有 UI 操作（添加、移除、修改属性）都标记为 `BlueprintAuthorityOnly`，只在服务端执行
2. **自动网络复制**：Widget 树通过 `FFastArraySerializer` 自动复制到客户端，客户端异步加载 UMG Widget 类并重建本地 UI
3. **统一的 Widget 树结构**：通过 `FUIFrameworkWidgetTree` 维护父子关系，支持完整的层级管理
4. **MVVM 集成**：基类 `UUIFrameworkWidget` 继承自 `UMVVMViewModelBase`，天然支持数据绑定模式

依赖 `ModelViewViewModel`（MVVM）、`LocalizableMessage`（本地化消息）和 `CommonUI`（通用UI系统）。

## 使用场景

- 你在做多人网络游戏，需要服务端控制玩家看到的 UI（如商店界面、任务面板、HUD 提示）→ 用 UIFramework
- 你需要服务端决定某个玩家是否能看到/交互某个 UI 元素 → 用 UIFramework 的 AuthorityOnly API
- 你需要 UI 状态在网络断线重连后自动同步恢复 → 用 UIFramework 的复制 Widget 树
- 你在使用 MVVM 模式构建 UI，且需要网络同步 → UIFramework 基于 `UMVVMViewModelBase`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddWidget` | 向玩家添加根级 UI Widget（仅服务端） | `UUIFrameworkPlayerComponent` |
| `RemoveWidget` | 从玩家移除根级 UI Widget（仅服务端） | `UUIFrameworkPlayerComponent` |
| `SetWidgetClass` | 设置 UserWidget 的 UMG 类（仅服务端） | `UUIFrameworkUserWidget` |
| `SetNamedSlot` | 向 UserWidget 命名插槽填入 Widget（仅服务端） | `UUIFrameworkUserWidget` |
| `SetContent` | 设置按钮内容 Widget（仅服务端） | `UUIFrameworkButton` |
| `SetContent` | 设置 SafeZone 内容 Widget（仅服务端） | `UUIFrameworkSafeZoneBox` |
| `AddWidget` | 向 StackBox 添加子 Widget（仅服务端） | `UUIFrameworkStackBox` |
| `AddWidget` | 向 CanvasBox 添加子 Widget（仅服务端） | `UUIFrameworkCanvasBox` |
| `AddWidget` | 向 Overlay 添加子 Widget（仅服务端） | `UUIFrameworkOverlay` |
| `SetMessage` / `SetTextSize` / `SetTextColor` 等 | 文本属性设置（仅服务端） | `UUIFrameworkTextBlock` |
| `SetTexture` / `SetTint` / `SetDesiredSize` | 图片属性设置（仅服务端） | `UUIFrameworkImageBlock` |
| `SetColor` / `SetDesiredSize` | 颜色块属性设置（仅服务端） | `UUIFrameworkColorBlock` |
| `SetVisibility` | 设置 Widget 可见性（可双向复制） | `UUIFrameworkWidget` |
| `SetEnabled` | 设置 Widget 是否启用（可双向复制） | `UUIFrameworkWidget` |
| `SetRenderOpacity` | 设置 Widget 渲染透明度（可双向复制） | `UUIFrameworkWidget` |

### 使用示例（蓝图描述）

**服务端创建 HUD（在服务端蓝图中）：**

1. 获取 `PlayerController` → 获取其 `UUIFrameworkPlayerComponent` 组件
2. 创建一个 `UUIFrameworkTextBlock`（或其他 Widget），设置文本内容
3. 创建一个 `FUIFrameworkGameLayerSlot` 结构体，设置 ZOrder、InputMode、Type
4. 将 TextBlock 设为 Slot 的 Widget
5. 调用 `PlayerComponent->AddWidget(Slot)` 添加到视口

**服务端创建按钮面板：**

1. 创建 `UUIFrameworkStackBox` 作为容器
2. 创建 `UUIFrameworkButton`，用 `SetContent` 填入内容 Widget
3. 创建 `FUIFrameworkStackBoxSlot`，将 Button 设为其 Widget
4. 调用 `StackBox->AddWidget(Slot)` 添加按钮到容器
5. 创建 `FUIFrameworkGameLayerSlot`，将 StackBox 设为其 Widget
6. 调用 `PlayerComponent->AddWidget(GameLayerSlot)` 添加到玩家

**处理按钮点击事件：**

1. 蓝图中绑定 `UUIFrameworkButton` 的 `OnClick` 委托
2. 回调参数为 `FUIFrameworkClickEventArgument`，包含 `PlayerController` 和 `Sender`

**使用 UserWidget 自定义布局：**

1. 创建 `UUIFrameworkUserWidget`，调用 `SetWidgetClass` 指向一个 UMG Widget 蓝图
2. 该 UMG 蓝图中定义 NamedSlot
3. 调用 `SetNamedSlot("SlotName", ChildWidget)` 将子 Widget 填入命名插槽

## C++ 用法

### 头文件引入

```cpp
#include "UIFramework/UIFWidget.h"
#include "UIFramework/UIFPlayerComponent.h"
#include "UIFramework/UIFModule.h"
#include "UIFramework/Widgets/UIFTextBlock.h"
#include "UIFramework/Widgets/UIFButton.h"
#include "UIFramework/Widgets/UIFStackBox.h"
#include "UIFramework/Widgets/UIFCanvasBox.h"
#include "UIFramework/Widgets/UIFOverlay.h"
#include "UIFramework/Widgets/UIFImageBlock.h"
#include "UIFramework/Widgets/UIFUserWidget.h"
#include "UIFramework/Types/UIFSlotBase.h"
```

### 基本用法

**在服务端添加 Widget 到玩家**（来自 `UIFPlayerComponent.h`）：

```cpp
// 仅在服务端执行
void AMyHUDActor::SetupUI(APlayerController* PC)
{
    // 获取 UIFrameworkPlayerComponent
    UUIFrameworkPlayerComponent* UIFComponent = PC->FindComponentByClass<UUIFrameworkPlayerComponent>();
    if (!UIFComponent) return;

    // 创建文本 Widget
    UUIFrameworkTextBlock* TextWidget = NewObject<UUIFrameworkTextBlock>(PC);
    TextWidget->SetTextSize(32.0f);
    TextWidget->SetTextColor(FLinearColor::White);

    // 配置游戏层插槽
    FUIFrameworkGameLayerSlot Slot;
    Slot.Widget = TextWidget;
    Slot.ZOrder = 10;
    Slot.InputMode = EUIFrameworkInputMode::Game;
    Slot.Type = EUIFrameworkGameLayerType::PlayerScreen;

    // 添加到玩家（仅服务端）
    UIFComponent->AddWidget(Slot);
}
```

**构建 Widget 树结构**（来自 `UIFStackBox.h` / `UIFWidget.h`）：

```cpp
// 创建 StackBox 容器
UUIFrameworkStackBox* StackBox = NewObject<UUIFrameworkStackBox>(PC);
StackBox->SetOrientation(EOrientation::Orient_Vertical);

// 创建按钮
UUIFrameworkButton* Button = NewObject<UUIFrameworkButton>(PC);
UUIFrameworkTextBlock* BtnText = NewObject<UUIFrameworkTextBlock>(PC);
BtnText->SetMessage(FLocalizableMessage()); // 设置本地化消息

FUIFrameworkSimpleSlot BtnContent;
BtnContent.Widget = BtnText;
BtnContent.Padding = FMargin(10.f);
Button->SetContent(BtnContent);

// 将按钮添加到 StackBox
FUIFrameworkStackBoxSlot StackSlot;
StackSlot.Widget = Button;
StackSlot.HorizontalAlignment = EHorizontalAlignment::HAlign_Center;
StackBox->AddWidget(StackSlot);

// 将 StackBox 添加为根 Widget
FUIFrameworkGameLayerSlot GameSlot;
GameSlot.Widget = StackBox;
GameSlot.ZOrder = 0;
GameSlot.Type = EUIFrameworkGameLayerType::PlayerScreen;
UIFComponent->AddWidget(GameSlot);
```

### 进阶用法

**使用 FUIFrameworkModule 管理 Widget 归属**（来自 `UIFModule.h`）：

```cpp
#include "UIFramework/UIFModule.h"

// 将 Widget 从一个父级迁移到另一个父级
void MoveWidget(UUIFrameworkWidget* Child, UUIFrameworkWidget* NewParent)
{
    // 检查是否可以附加
    FUIFrameworkParentWidget ParentWrapper(NewParent);
    if (FUIFrameworkModule::AuthorityCanWidgetBeAttached(ParentWrapper, Child))
    {
        // 自动处理复制所有者变更和子树重建
        UUIFrameworkWidget* Result = FUIFrameworkModule::AuthorityAttachWidget(ParentWrapper, Child);
    }
}

// 从父级分离 Widget
void DetachWidget(UUIFrameworkWidget* Child)
{
    FUIFrameworkModule::AuthorityDetachWidgetFromParent(Child);
}
```

**自定义 Presenter（控制 Widget 如何添加到视口）**（来自 `UIFPresenter.h`）：

```cpp
#include "UIFramework/UIFPresenter.h"

// 自定义 Presenter 类
UCLASS()
class UMyCustomPresenter : public UUIFrameworkPresenter
{
    GENERATED_BODY()

public:
    virtual void AddToViewport(UWidget* UMGWidget, const FUIFrameworkGameLayerSlot& Slot) override
    {
        // 自定义添加到视口的逻辑
        if (UUserWidget* UserWidget = Cast<UUserWidget>(UMGWidget))
        {
            UserWidget->AddToViewport(Slot.ZOrder);
        }
    }

    virtual void RemoveFromViewport(FUIFrameworkWidgetId WidgetId) override
    {
        // 自定义移除逻辑
    }

    virtual void FocusWidget(UWidget* UMGWidget) override
    {
        // 自定义焦点逻辑
    }
};

// 在初始化时设置自定义 Presenter
void Setup()
{
    FUIFrameworkModule::SetPresenterClass(UMyCustomPresenter::StaticClass());
}
```

**监听 Widget 树变化**（来自 `UIFWidgetTree.h`）：

```cpp
// 绑定 Widget 树事件
void AMyActor::BindTreeEvents(UUIFrameworkPlayerComponent* UIFComp)
{
    FUIFrameworkWidgetTree& Tree = UIFComp->GetWidgetTree();

    Tree.AuthorityOnWidgetAdded.AddUObject(this, &AMyActor::OnWidgetAdded);
    Tree.AuthorityOnWidgetRemoved.AddUObject(this, &AMyActor::OnWidgetRemoved);
    Tree.LocalOnWidgetAdded.AddUObject(this, &AMyActor::OnLocalWidgetAdded);
}

void OnWidgetAdded(UUIFrameworkWidget* Widget)
{
    // Widget 在服务端被添加到树
}

void OnWidgetRemoved(UUIFrameworkWidget* Widget)
{
    // Widget 在服务端被从树移除
}

void OnLocalWidgetAdded(UUIFrameworkWidget* Widget)
{
    // Widget 在客户端被复制并添加
    // 此时 LocalGetUMGWidget() 可能还未就绪
}
```

**处理复制就绪状态**（来自 `UIFWidget.h`）：

```cpp
// 等待 Widget 复制就绪后再操作 UMG Widget
void OnLocalWidgetAdded(UUIFrameworkWidget* Widget)
{
    // 方法一：手动检查并异步加载
    if (Widget->LocalIsReplicationReady())
    {
        TSharedPtr<FStreamableHandle> Handle = Widget->AsyncLoadWidgetClass();
        // 加载完成后 UMG Widget 会被创建
    }

    // 方法二：使用便捷方法
    UWidget* UMGWidget = Widget->LocalGetOrCreateUMGWidgetIfReady();
    if (UMGWidget)
    {
        // UMG Widget 已就绪
    }
}
```

## Demo 示例

### 自定义 UIFramework Widget（C++ 扩展）

**MyUIModule.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyUIModule.generated.h"

class UUIFrameworkPlayerComponent;
class UUIFrameworkTextBlock;
class UUIFrameworkButton;
class UUIFrameworkStackBox;

/**
 * 管理 UIFramework UI 的示例组件
 */
UCLASS(ClassGroup=(UI), meta=(BlueprintSpawnableComponent))
class UMyUIModule : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    /** 创建示例 HUD（仅服务端调用） */
    UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "UI")
    void CreateDemoHUD();

    /** 移除 HUD（仅服务端调用） */
    UFUNCTION(BlueprintCallable, BlueprintAuthorityOnly, Category = "UI")
    void DestroyDemoHUD();

private:
    UPROPERTY()
    TObjectPtr<UUIFrameworkStackBox> RootContainer;

    UPROPERTY()
    TObjectPtr<UUIFrameworkTextBlock> StatusText;

    UPROPERTY()
    TObjectPtr<UUIFrameworkButton> ActionButton;

    UPROPERTY()
    TObjectPtr<UUIFrameworkTextBlock> ButtonLabel;

    UFUNCTION()
    void OnActionButtonClicked(FUIFrameworkClickEventArgument Args);
};
```

**MyUIModule.cpp**

```cpp
#include "MyUIModule.h"
#include "UIFramework/UIFPlayerComponent.h"
#include "UIFramework/UIFModule.h"
#include "UIFramework/Widgets/UIFTextBlock.h"
#include "UIFramework/Widgets/UIFButton.h"
#include "UIFramework/Widgets/UIFStackBox.h"
#include "UIFramework/Types/UIFSlotBase.h"

void UMyUIModule::BeginPlay()
{
    Super::BeginPlay();

    // 仅服务端创建 UI
    if (GetOwner() && GetOwner()->HasAuthority())
    {
        CreateDemoHUD();
    }
}

void UMyUIModule::CreateDemoHUD()
{
    AActor* Owner = GetOwner();
    if (!Owner) return;

    // 获取 PlayerController
    APlayerController* PC = nullptr;
    if (APawn* Pawn = Cast<APawn>(Owner))
    {
        PC = Cast<APlayerController>(Pawn->GetController());
    }
    else
    {
        PC = Cast<APlayerController>(Owner);
    }
    if (!PC) return;

    UUIFrameworkPlayerComponent* UIFComp = PC->FindComponentByClass<UUIFrameworkPlayerComponent>();
    if (!UIFComp) return;

    // 创建根容器 StackBox（垂直排列）
    RootContainer = NewObject<UUIFrameworkStackBox>(PC);
    RootContainer->SetOrientation(Orient_Vertical);

    // 创建状态文本
    StatusText = NewObject<UUIFrameworkTextBlock>(PC);
    StatusText->SetTextSize(28.0f);
    StatusText->SetTextColor(FLinearColor::Green);

    FUIFrameworkStackBoxSlot StatusSlot;
    StatusSlot.Widget = StatusText;
    StatusSlot.HorizontalAlignment = HAlign_Center;
    StatusSlot.Padding = FMargin(10.f);
    RootContainer->AddWidget(StatusSlot);

    // 创建按钮
    ActionButton = NewObject<UUIFrameworkButton>(PC);
    ButtonLabel = NewObject<UUIFrameworkTextBlock>(PC);
    ButtonLabel->SetTextSize(20.0f);
    ButtonLabel->SetTextColor(FLinearColor::White);

    FUIFrameworkSimpleSlot ButtonContent;
    ButtonContent.Widget = ButtonLabel;
    ButtonContent.Padding = FMargin(20.f, 10.f);
    ActionButton->SetContent(ButtonContent);

    // 绑定按钮点击事件
    ActionButton->OnClick.AddUObject(this, &UMyUIModule::OnActionButtonClicked);

    FUIFrameworkStackBoxSlot ButtonSlot;
    ButtonSlot.Widget = ActionButton;
    ButtonSlot.HorizontalAlignment = HAlign_Center;
    ButtonSlot.Padding = FMargin(10.f);
    RootContainer->AddWidget(ButtonSlot);

    // 将根容器添加到游戏层
    FUIFrameworkGameLayerSlot GameSlot;
    GameSlot.Widget = RootContainer;
    GameSlot.ZOrder = 100;
    GameSlot.InputMode = EUIFrameworkInputMode::Game;
    GameSlot.Type = EUIFrameworkGameLayerType::PlayerScreen;
    UIFComp->AddWidget(GameSlot);
}

void UMyUIModule::DestroyDemoHUD()
{
    AActor* Owner = GetOwner();
    if (!Owner) return;

    APlayerController* PC = nullptr;
    if (APawn* Pawn = Cast<APawn>(Owner))
    {
        PC = Cast<APlayerController>(Pawn->GetController());
    }
    else
    {
        PC = Cast<APlayerController>(Owner);
    }
    if (!PC) return;

    UUIFrameworkPlayerComponent* UIFComp = PC->FindComponentByClass<UUIFrameworkPlayerComponent>();
    if (!UIFComp || !RootContainer) return;

    UIFComp->RemoveWidget(RootContainer);
}

void UMyUIModule::OnActionButtonClicked(FUIFrameworkClickEventArgument Args)
{
    // 服务端处理按钮点击
    // Args.PlayerController 是点击按钮的玩家控制器
    // Args.Sender 是发送事件的 Widget
    UE_LOG(LogTemp, Log, TEXT("Button clicked by %s"), *GetNameSafe(Args.PlayerController));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ModelViewViewModel` | Widget 基类继承自 UMVVMViewModelBase，提供 MVVM 数据绑定支持 |
| `LocalizableMessage` | 文本 Widget 使用 FLocalizableMessage 进行本地化消息支持 |
| `CommonUI` | 通用 UI 基础设施，InputAction 处理等 |
| `EnhancedInput` | 按钮 Widget 支持触发输入动作（TriggeringInputAction） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统迁移到 UE_LOGF 宏 |
| 2026-03-23 | `dead1658` | Verse UI Input: expose Back input action internally. | 为 Verse UI 输入暴露返回键动作 |
| 2026-03-10 | `3a8c54e8` | Implement UIFrameworkTouchActionWrapperWidget. New widget that allows the user to wrap any other widget to receive touch input actions. | 新增触摸输入包装 Widget，支持触摸输入动作 |
| 2026-03-10 | `6cad334d` | Fix crash by direct loading default contant on designer preview, canvas preview creates and discards | 修复设计器预览时直接加载默认内容导致的崩溃 |
| 2026-02-18 | `502110e2` | Renaming UEFN Custom Button to Custom Button, removed UEFN_Custom_Button blueprint not needed anymore | 重命名 UEFN 自定义按钮，移除废弃蓝图 |

### 维护评价

- **创建时间**：2022-07-18，约 3 年历史
- **实验性状态**：`EnabledByDefault=false`，仍为实验性插件
- **维护活跃度**：活跃维护中。2026 年有多次功能性更新，包括新增触摸输入 Widget、Verse UI 集成、bug 修复等
- **架构成熟度**：设计完整，包含权威/本地分离、异步 Widget 类加载、FastArray 复制、MVVM 集成、自定义 Presenter 等成熟机制
- **已知限制**：实验性插件，API 可能在未来版本中发生变化；部分 Widget 类型有限（缺少常见的 Slider、CheckBox 等）
- **推荐程度**：如果你正在开发需要服务端控制 UI 的多人游戏，这个框架提供了良好的基础架构。但由于仍为实验性，生产环境使用需谨慎评估 API 稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UIFramework)
- 官方文档：无（.uplugin 中 DocsURL 为空）