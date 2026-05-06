# Editor Performance

> Plugin that provides Editor Performance feedback to developers

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器性能反馈 |
| 分类 | Performance |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `EditorPerformance` (Editor), `StallLogSubsystem` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-09-15 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorPerformance) | |

## 用途

Editor Performance 插件旨在为开发者提供编辑器运行时性能的实时反馈。其核心功能是**编辑器卡顿检测与可视化**：当编辑器发生阻塞（stall）时，自动记录卡顿事件并展示给开发者，帮助定位性能瓶颈。该插件通过 `UStallLogSubsystem` 子系统订阅编辑器主线程的卡顿事件，并将历史记录保存在内存中，开发者可通过编辑器 UI 面板查看卡顿详情（如持续时间、发生位置、调用堆栈等）。此插件在开发大型项目或复杂编辑器功能时尤为有用，让开发者能够及时发现并优化导致编辑器卡顿的代码。

## 使用场景

- 你在开发编辑器插件或自定义编辑器工具，发现编辑器频繁“死掉”几秒钟 → 用该插件的卡顿日志分析原因。
- 你的项目加载大量资源或执行耗时操作，希望量化卡顿发生的频率和时长 → 开启该插件观察性能趋势。
- 团队需要统一监控编辑器性能，在新功能上线前检查是否引入额外卡顿 → 依赖该插件作为标准反馈机制。

## 蓝图用法

该插件所有功能均在 C++ 和编辑器层面实现，未暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 属性。因此蓝图不可直接使用。你需要通过 C++ 或编辑器 UI 交互。

## C++ 用法

### 头文件引入

```cpp
#include "StallLogSubsystem.h"
```

### 基本用法

`UStallLogSubsystem` 是一个 `UEditorSubsystem`，在编辑器启动时自动创建。你可以通过 `GEditor->GetEditorSubsystem<UStallLogSubsystem>()` 获取实例。该子系统主要负责管理卡顿日志和提供 UI 面板。

**获取卡顿日志面板**：  
创建编辑器选项卡时，调用 `CreateStallLogPanel()` 获得一个 `SWidget`，可直接嵌入到你自己的编辑器 UI 中。

```cpp
// 来源：Engine/Plugins/Experimental/EditorPerformance/Source/StallLogSubsystem/Public/StallLogSubsystem.h

// 在某个编辑器模块中获取子系统并创建面板
UStallLogSubsystem* StallSubsystem = GEditor->GetEditorSubsystem<UStallLogSubsystem>();
if (StallSubsystem)
{
    TSharedRef<SWidget> StallPanel = StallSubsystem->CreateStallLogPanel();
    // 将 StallPanel 添加到 Slate 布局中
}
```

### 进阶用法

如果你希望自定义卡顿检测的处理逻辑，可以继承 `UStallLogSubsystem` 并重写 `ShouldCreateSubsystem`、`Initialize`、`Deinitialize`。但大部分场景无需自定义，插件默认会注册 `OnStallDetectedDelegate` 和 `OnStallCompletedDelegate` 的监听。

> 注意：`UStallLogSubsystem` 内部使用 `FStallLogHistory` 存储历史记录，该类型位于私有实现中，不暴露给用户。因此你无法直接遍历日志，只能通过内置面板查看。

## Demo 示例

以下是一个完整的 C++ 最小示例，展示如何在编辑器模块中打开一个带有卡顿日志面板的窗口。

**MyEditorModule.h**

```cpp
#pragma once
#include "Modules/ModuleInterface.h"
#include "Templates/SharedPointer.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<class SDockTab> MyTab;
    void OnSpawnMyTab();
};
```

**MyEditorModule.cpp**

```cpp
#include "MyEditorModule.h"
#include "StallLogSubsystem.h"
#include "LevelEditor.h"
#include "Widgets/Docking/SDockTab.h"
#include "Widgets/DeclarativeSyntaxSupport.h"
#include "Framework/MultiBox/MultiBoxBuilder.h"

IMPLEMENT_MODULE(FMyEditorModule, MyEditorModule)

void FMyEditorModule::StartupModule()
{
    // 注册一个按钮到 LevelEditor 菜单
    FLevelEditorModule& LevelEditorModule = FModuleManager::LoadModuleChecked<FLevelEditorModule>("LevelEditor");
    TSharedPtr<FExtender> MenuExtender = MakeShareable(new FExtender);
    MenuExtender->AddMenuExtension(
        "WindowLayout",
        EExtensionHook::After,
        nullptr,
        FMenuExtensionDelegate::CreateRaw(this, &FMyEditorModule::OnSpawnMyTab)
    );
    LevelEditorModule.GetMenuExtensibilityManager()->AddExtender(MenuExtender);
}

void FMyEditorModule::ShutdownModule()
{
    if (MyTab.IsValid())
    {
        FGlobalTabmanager::Get()->InvokeTab(MyTab->GetTabIdPtr());
    }
}

void FMyEditorModule::OnSpawnMyTab()
{
    // 打开包含 StallLogPanel 的新标签页
    FGlobalTabmanager::Get()->RegisterNomadTabSpawner("MyStallTab", FOnSpawnTab::CreateLambda([](const FSpawnTabArgs& Args)
    {
        UStallLogSubsystem* StallSubsystem = GEditor->GetEditorSubsystem<UStallLogSubsystem>();
        if (StallSubsystem)
        {
            return SNew(SDockTab)
                .TabRole(ETabRole::NomadTab)
                [
                    StallSubsystem->CreateStallLogPanel()
                ];
        }
        return SNew(SDockTab).TabRole(ETabRole::NomadTab)[SNew(STextBlock).Text(FText::FromString("StallLogSubsystem not available"))];
    }));
    FGlobalTabmanager::Get()->TryInvokeTab(FName("MyStallTab"));
}
```

**MyEditorModule.Build.cs**（供参考）

```csharp
using UnrealBuildTool;

public class MyEditorModule : ModuleRules
{
    public MyEditorModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "Slate",
            "SlateCore",
            "EditorSubsystem",  // 直接依赖
            "StallLogSubsystem" // 依赖该插件模块
        });

        PrivateDependencyModuleNames.AddRange(new string[]
        {
            "LevelEditor",
            "UnrealEd"
        });
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `StallLogSubsystem` | 编辑器性能子系统的核心实现，依赖 `EditorSubsystem`、`Slate` |
| `LevelEditor` | 用于注册标签页和菜单（示例中需要） |
| `UnrealEd` | 提供编辑器框架（示例中需要） |

> **说明**：官方依赖已省略“Core/CoreUObject/Engine/Slate/SlateCore”等常见模块。实际插件的 `StallLogSubsystem` 模块自身需链接 `EditorSubsystem`（编辑器子系统基类）和 `Projects` 等。若直接使用 `UStallLogSubsystem`，你需要在你的模块 Build.cs 中添加 `"StallLogSubsystem"` 到 `PublicDependencyModuleNames`。

## 维护状态

### 近期更新

- 2025-09-24 fe567f78 — Editor Diagnostics: Made the status and notification more reactive
- 2025-09-24 193e083c — Editor Diagnostics
- 2025-09-23 5c90eb49 — Editor Diagnostics status bar styling
- 2025-09-15 b017b708 — Editor Performance Dialog:
- 2025-09-15 f0e8d613 — Enable Editor Performance Tools by default

### 维护评价

该插件于 2025 年 9 月创建，非常新，且创建后数天内就有多次提交，主要涉及“Editor Diagnostics”功能（可能与卡顿日志面板的 UI 和通知相关）。插件目前标记为 Beta 吗？.uplugin 中 `IsBetaVersion=false` ，`EnabledByDefault=true`，说明它已经是一个默认启用的成熟功能。尽管代码量小（12 个源文件），但功能专一，维护活跃。当前没有已知的废弃标记。推荐在编辑器扩展开发中使用。

> ⚠️ 注意：插件位于 `Experimental` 目录，但 `IsBetaVersion=false`，故不应视为实验性，更可能是从实验阶段毕业并默认启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorPerformance)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorPerformance/Tests)（如果存在）
- 官方文档：暂无