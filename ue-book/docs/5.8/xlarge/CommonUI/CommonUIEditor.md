# Common UI Plugin

> A repository for game independent UI elements.

| 属性 | 值 |
|---|---|
| 中文名 | 通用UI框架 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据表资产、材质模板） |
| 模块 | `CommonUI` (Runtime), `CommonInput` (Runtime), `CommonUIEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2023-05-02 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/CommonUI) | |

## 用途

CommonUI 是一套**与具体游戏无关的跨平台 UI 框架**，解决的核心问题是：**同一套 UI 如何在不同输入设备（键鼠、手柄、触屏）下都能良好工作**。

传统 UMG 的输入处理假设玩家使用鼠标，一旦需要支持手柄导航或触屏操作，开发者需要大量自定义代码。CommonUI 通过以下机制解决这个问题：

- **输入路由**：UI Widget 可以根据当前激活的输入设备自动切换显示和交互模式
- **焦点导航系统**：提供类似主机游戏的焦点导航（上下左右切换焦点），支持 `Proximate Entry Navigation`（近邻导航）和 `Navigation Guard`（导航保护）
- **虚拟指针（Virtual Pointer）**：为手柄用户提供模拟光标，使其可以像鼠标一样与 UI 交互
- **输入动作数据表**：将 Enhanced Input 动作映射为数据表驱动的配置，方便动态绑定
- **视频播放器**：内置支持视频播放的 Widget，带完整的播放控制 UI

该插件从 `Experimental` 目录迁出进入 `Beta`（见首次提交记录），在 Epic 内部被 Fortnite 等项目重度使用，代表了 UE5 UI 开发的推荐实践。

**注意**：`EnabledByDefault=false`，需要在项目设置中手动启用。

## 使用场景

- 你正在开发一款需要同时支持 PC 和主机平台的游戏 → 用 CommonUI 处理手柄/键鼠/触屏的 UI 交互差异
- 你需要 UI 焦点导航（类似 Xbox/PlayStation 菜单的上下切换） → 用 CommonUI 的焦点导航系统
- 你希望不同平台显示不同的操作提示（PC 显示"点击"，手柄显示"A键"） → 用 CommonInput 的输入设备自动检测和提示图标切换
- 你需要在 UI 中嵌入视频播放器并支持手柄控制 → 用 CommonVideoPlayer
- 你希望用数据表驱动方式管理输入动作映射，而不是在每个 Widget 里硬编码 → 用 CommonGenericInputActionDataTable

## 蓝图用法

### 核心节点

CommonUI 提供的蓝图 API 主要围绕输入路由、焦点管理和视图栈展开：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetInputMode` | 设置 Widget 的输入模式（鼠标/手柄/触屏） | `UCommonActivatableWidget` |
| `IsActivated` | 查询 Widget 是否处于激活状态 | `UCommonActivatableWidget` |
| `RegisterScrollReceiver` | 注册滚动接收器，处理手柄摇杆滚动 | `UCommonActivatablePanel` |
| `GetInputActionDataTable` | 获取当前输入设备对应的输入动作数据表 | `UCommonInputSubsystem` |
| `GetCurrentInputDevice` | 获取当前活跃的输入设备类型 | `UCommonInputSubsystem` |

### 输入动作数据表

`CommonGenericInputActionDataTable` 是一个数据表资产类型，用于将 Enhanced Input 动作与 UI 显示图标关联：

1. 在 Content Browser 中右键 → **Miscellaneous** → **DataTable** → 选择 `CommonGenericInputActionDataTable`
2. 在数据表中为每个输入动作配置不同平台/设备的操作提示图标
3. 在 Widget 中通过 `GetInputActionDataTable` 动态获取当前设备对应的图标

### 视频播放器 Widget

`CommonVideoPlayer` 在 Details 面板中提供专用自定义界面：

- 播放/暂停/反转控制按钮
- 时间轴滑块（可拖拽跳转）
- 前进/后退单步控制
- 静音切换按钮

## C++ 用法

### 头文件引入

```cpp
#include "CommonUIEditorModule.h"  // 编辑器模块
#include "CommonGenericInputActionDataTableFactory.h"  // 数据表工厂
```

### 基本用法 — 自定义资产定义

CommonUI 通过 `UAssetDefinition_CommonGenericInputActionDataTable` 为输入动作数据表提供编辑器集成：

```cpp
// 来源: Private/AssetDefinition_CommonGenericInputActionDataTable.h
// 注册自定义数据表资产在 Content Browser 中的显示

UCLASS()
class UAssetDefinition_CommonGenericInputActionDataTable : public UAssetDefinition_DataTable
{
    GENERATED_BODY()
public:
    // 资产显示名称
    virtual FText GetAssetDisplayName() const override
    {
        return NSLOCTEXT("AssetDefinition", "...", "Common UI InputActionDataTable");
    }

    // 资产颜色标记（棕色）
    virtual FLinearColor GetAssetColor() const override
    {
        return FColor(139.f, 69.f, 19.f);
    }

    // 关联的资产类型
    virtual TSoftClassPtr<UObject> GetAssetClass() const override
    {
        return UCommonGenericInputActionDataTable::StaticClass();
    }

    // 资产分类路径：Data > Data Table
    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override;
};
```

### 基本用法 — 视频播放器编辑器自定义

`FCommonVideoPlayerCustomization` 为 `CommonVideoPlayer` 提供 Details 面板自定义：

```cpp
// 来源: Private/CommonVideoPlayerCustomization.h
// 自定义视频播放器的属性面板

class FCommonVideoPlayerCustomization : public IDetailCustomization
{
public:
    // 注册方式：
    // PropertyModule.RegisterCustomClassLayout(
    //     UCommonVideoPlayer::StaticClass()->GetFName(),
    //     FOnGetDetailCustomizationInstance::CreateStatic(
    //         &FCommonVideoPlayerCustomization::MakeInstance));

    virtual void CustomizeDetails(IDetailLayoutBuilder& DetailLayout) override;

private:
    // 播放控制回调
    FReply HandlePlayClicked();
    FReply HandlePauseClicked();
    FReply HandleReverseClicked();
    FReply HandleGoToStartClicked();
    FReply HandleGoToEndClicked();
    FReply HandleBackwardStep();
    FReply HandleForwardStep();

    // 时间轴
    TOptional<float> GetMaxPlaybackTimeValue() const;
    TOptional<float> GetPlaybackTimeValue() const;
    void HandlePlaybackTimeCommitted(float NewTime, ETextCommit::Type);

    // 静音控制
    TSharedRef<SWidget> HandleCreateMuteToggleWidget() const;
    FReply HandleToggleMuteClicked() const;
    const FSlateBrush* GetMuteToggleIcon() const;
};
```

### 基本用法 — 数据表工厂

```cpp
// 来源: Public/CommonGenericInputActionDataTableFactory.h
// 工厂类用于在编辑器中创建 CommonGenericInputActionDataTable 资产

UCLASS()
class UCommonGenericInputActionDataTableFactory : public UFactory
{
    GENERATED_UCLASS_BODY()

    // 创建新资产实例
    virtual UObject* FactoryCreateNew(
        UClass* Class,
        UObject* InParent,
        FName Name,
        EObjectFlags Flags,
        UObject* Context,
        FFeedbackContext* Warn) override;
};
```

### 编辑器模块注册

```cpp
// 来源: Public/CommonUIEditorModule.h

class FCommonUIEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;   // 注册资产定义、属性自定义等
    virtual void ShutdownModule() override;  // 反注册
};
```

## Demo 示例

### 自定义输入动作数据表资产处理器

```cpp
// MyInputActionHandler.h
#pragma once

#include "CoreMinimal.h"
#include "CommonGenericInputActionDataTable.h"

class FMyInputActionHandler
{
public:
    // 加载并查询输入动作数据表
    static void QueryInputAction(const UCommonGenericInputActionDataTable* DataTable, FName ActionName);
};
```

```cpp
// MyInputActionHandler.cpp
#include "MyInputActionHandler.h"

void FMyInputActionHandler::QueryInputAction(
    const UCommonGenericInputActionDataTable* DataTable, FName ActionName)
{
    if (!DataTable)
    {
        UE_LOG(LogTemp, Warning, TEXT("InputActionDataTable is null"));
        return;
    }

    // 数据表会根据当前输入设备自动提供对应的图标和映射
    // 实际使用中通常通过 CommonInputSubsystem 自动处理
    UE_LOG(LogTemp, Log, TEXT("Querying input action: %s"), *ActionName.ToString());
}
```

## 模块依赖

CommonUI 依赖以下插件（`.uplugin` 中声明）：

| 插件 | 用途 |
|---|---|
| `EnhancedInput` | 输入动作系统，CommonUI 的输入映射基于 Enhanced Input |
| `GameplayTagsEditor` | 游戏标签编辑器支持，用于输入设备/平台标签化管理 |
| `EngineAssetDefinitions` | 资产定义框架，用于自定义资产在 Content Browser 中的显示 |

编译时依赖（从 Build.cs 推断）：

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 运行时输入处理 |
| `GameplayTags` | 输入设备和平台的标签分类 |
| `MediaAssets` | 视频播放器功能 |
| `MediaUtils` | 视频播放底层工具 |
| `AssetDefinition` | 编辑器资产定义注册 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `ea0fcb96` | [UMG/Slate] Proximate Entry Navigation - ScrollIntoView Local Space & Intra-Entry List Interior Guard | 修复近邻导航的滚动到视图功能，使用局部空间计算并增加列表内部导航保护 |
| 2026-05-26 | `356fcc56` | [Virtual Pointer] Ignore the synthetic mouse-move event that UCommonInputSubsystem::SetCursorPositio | 虚拟指针模式下忽略 SetCursorPosition 产生的合成鼠标移动事件 |
| 2026-05-25 | `a10370d0` | [Virtual Pointer] FCommonAnalogCursor::RefreshCursorVisibility: gate viewport cursor writes on actua | 虚拟指针刷新可见性时，仅在实际变化时才写入视口光标状态，避免冗余更新 |
| 2026-05-22 | `e3f56aa5` | [Virtual Pointer] In VP mode, clamp the cursor to the viewport only when gamepad is driving it; mous | 虚拟指针模式下，仅在手柄驱动时将光标限制在视口范围内，鼠标移动时不做限制 |
| 2026-05-20 | `4bcb727a` | CommonListView, SCommonTileView - Repair non-proximate pathway to not mutate focus when there is no | 修复 ListView/TileView 在非近邻导航路径下，无有效焦点目标时错误修改焦点的问题 |

### 维护评价

- **活跃维护**：最近一周内有多次实质性更新（2026-05-20 ~ 05-26），说明仍在积极开发
- **更新方向**：主要集中在**虚拟指针（Virtual Pointer）**和**焦点导航系统**两个核心子系统的打磨，包括 Bug 修复和行为优化
- **成熟度**：从 Experimental 移出进入 Beta（非正式版），但 Epic 内部大规模使用（Fortnite），实际成熟度较高
- **已知限制**：`EnabledByDefault=false` 需要手动启用；依赖 EnhancedInput 插件，如果项目未使用 EnhancedInput 会增加额外依赖
- **推荐程度**：**强烈推荐**。如果你的游戏需要支持多种输入设备或跨平台发布，CommonUI 是 Epic 官方推荐的 UI 框架，比自己实现手柄导航/输入切换要健壮得多

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/CommonUI)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [CommonUI 概述（UE 官方文档）](https://docs.unrealengine.com/5.8/en-US/common-ui-plugin-in-unreal-engine/)（社区维护）

---

> **插件规模**：本插件包含 154 个源文件，属于 **large** 级别。以上文档涵盖了核心模块和编辑器集成的概览。完整的 CommonUI 框架还包含 `CommonUI`（运行时核心：ActivatableWidget、ActivatablePanel、ActionRouter、VideoPlayer 等）和 `CommonInput`（输入设备抽象、平台输入映射、AnalogCursor、CommonInputSubsystem 等）两个大型运行时模块，建议结合源码和官方示例项目深入学习。