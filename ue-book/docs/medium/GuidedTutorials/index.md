# Guided Tutorials

> Adds classes and content that support running guided tutorials within the editor UI.

| 属性 | 值 |
|---|---|
| 分类 | Learning |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（教程资产、图标、材质、动画蓝图、骨架网格体） |
| 模块 | `IntroTutorials` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-02-16 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/GuidedTutorials) | |

## 用途

Guided Tutorials 是 UE5 编辑器内置的交互式教程框架。它提供了一套完整的 UI 系统，让开发者可以创建分步骤（stage-by-stage）的引导式教程，覆盖编辑器的各个功能区域。

核心能力：
- **教程资产**：通过 `UEditorTutorial` 蓝图资产定义教程的各个阶段，支持富文本、UDN 文档摘录和普通文本
- **UI 高亮与锚定**：教程内容可以锚定到编辑器中的特定控件（NamedWidget）或资产（Asset），并显示动画高亮效果
- **教程浏览器**：内置的 `STutorialsBrowser` 提供分类浏览、搜索和面包屑导航
- **上下文感知**：根据当前编辑器上下文（如关卡编辑器、蓝图编辑器）自动推荐相关教程
- **状态持久化**：通过 `UTutorialStateSettings` 记录用户已看过的教程，避免重复展示
- **教程链式跳转**：支持 `NextTutorial` 和 `PreviousTutorial` 实现教程之间的前后导航
- **启动教程**：可在编辑器启动时自动弹出欢迎教程

这个插件默认是**禁用**的（`Installed: false`），需要在插件管理器中手动启用。Epic 使用此框架制作了引擎自带的入门教程（如关卡编辑器教程、蓝图教程等）。

## 使用场景

- 你想为你的 UE5 项目或插件创建交互式教程 → 使用 Guided Tutorials
- 你在做一个团队内部工具，需要引导新成员熟悉编辑器操作 → 创建 `UEditorTutorial` 蓝图
- 你想在编辑器启动时向用户展示欢迎引导 → 配置 `StartupTutorial` 设置
- 你需要在蓝图编辑器中嵌入上下文相关的帮助内容 → 使用 `TutorialContext` 系统
- 你想为项目创建一个教程浏览器入口 → 调用 `CreateTutorialsWidget`

## 蓝图用法

`UEditorTutorial` 是 `Blueprintable` 的，可以创建蓝图子类来定义教程内容。所有教程都是在蓝图编辑器中配置的。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BeginTutorial` | 启动一个教程（可选是否重启） | `UEditorTutorial` |
| `GoToNextTutorialStage` | 跳转到下一个教程阶段 | `UEditorTutorial` |
| `GoToPreviousTutorialStage` | 跳转到上一个教程阶段 | `UEditorTutorial` |
| `OpenAsset` | 在编辑器中打开一个资产 | `UEditorTutorial` |
| `GetActorReference` | 通过路径获取场景中的 Actor 引用 | `UEditorTutorial` |
| `SetEngineFolderVisibilty` | 设置 Content Browser 中 Engine 文件夹的可见性 | `UEditorTutorial` |
| `GetEngineFolderVisibilty` | 获取 Content Browser 中 Engine 文件夹的可见性 | `UEditorTutorial` |

### 事件（BlueprintImplementableEvent）

| 事件 | 说明 |
|---|---|
| `OnTutorialStageStarted` | 教程阶段开始时触发，参数为阶段名称 |
| `OnTutorialStageEnded` | 教程阶段结束时触发 |
| `OnTutorialLaunched` | 教程被启动时触发 |
| `OnTutorialClosed` | 教程被关闭时触发 |

### 教程资产配置

创建一个 `UEditorTutorial` 蓝图子类后，需要在 Details 面板中配置以下内容：

1. **Tutorial 属性**：
   - `Title`：教程标题
   - `Category`：分类（如 "Editor Quickstart"）
   - `Icon` / `Texture`：浏览器中显示的图标
   - `SortOrder`：排序优先级
   - `SummaryContent`：浏览器中的摘要描述
   - `bIsStandalone`：独立教程不显示导航按钮
   - `AssetToUse`：教程要附加到的资产
   - `bHideInBrowser`：在浏览器中隐藏

2. **Stages 数组**：每个 `FTutorialStage` 包含：
   - `Name`：阶段标识名
   - `Content`：主要内容（支持 RichText、Text、UDNExcerpt）
   - `WidgetContent`：绑定到特定控件的内容数组
   - `NextButtonText` / `BackButtonText`：按钮文本
   - `PlatformsToTest`：平台过滤

3. **链接**：
   - `PreviousTutorial`：上一个教程
   - `NextTutorial`：下一个教程

### 使用示例（蓝图描述）

创建一个简单的编辑器教程：

1. 在 Content Browser 右键 → Blueprint Class → 选择 `EditorTutorial` 作为父类
2. 打开蓝图，在 Details 面板设置 `Title` 为 "My First Tutorial"
3. 设置 `Category` 为 "My Tutorials"
4. 在 `Stages` 数组中添加元素：
   - 第一个 Stage：设置 `Content.Text` 为欢迎文本，添加 `WidgetContent` 锚定到特定编辑器控件
   - 第二个 Stage：设置另一个操作步骤的内容
5. 保存蓝图资产
6. 通过 Help → Tutorials 菜单即可看到你的教程出现在浏览器中

## C++ 用法

### 头文件引入

```cpp
#include "IIntroTutorials.h"
#include "EditorTutorial.h"
```

### 基本用法

通过模块接口启动教程：

```cpp
// 获取模块接口
IIntroTutorials& IntroTutorials = IIntroTutorials::Get();

// 通过资产路径启动教程
IntroTutorials.LaunchTutorial(TEXT("/Game/Tutorials/MyTutorial.MyTutorial"));

// 通过 UEditorTutorial 对象启动教程（重启模式）
UEditorTutorial* Tutorial = GetMyTutorialObject();
IntroTutorials.LaunchTutorial(Tutorial, IIntroTutorials::TST_RESTART);

// 关闭所有教程内容
IntroTutorials.CloseAllTutorialContent();
```

### 进阶用法

创建上下文感知的教程入口 widget：

```cpp
// 在自定义编辑器中创建教程入口
IIntroTutorials& IntroTutorials = IIntroTutorials::Get();

// 创建教程 widget 并嵌入到你的编辑器 UI 中
TSharedRef<SWidget> TutorialWidget = IntroTutorials.CreateTutorialsWidget(
    FName("MyCustomEditor"),    // 上下文名称
    MyEditorWindow              // 所在窗口
);

// 注册自定义教程分类
FTutorialCategory NewCategory;
NewCategory.Identifier = TEXT("MyPlugin.Feature");
NewCategory.Title = NSLOCTEXT("MyPlugin", "FeatureCategory", "Feature Tutorials");
NewCategory.Description = NSLOCTEXT("MyPlugin", "FeatureDesc", "Learn about our feature");
IntroTutorials.RegisterCategory(NewCategory);
```

使用 `UEditorTutorial` 的静态方法：

```cpp
// 在教程蓝图中可调用的 C++ 方法
UEditorTutorial::BeginTutorial(MyTutorial, true);  // 启动教程
UEditorTutorial::GoToNextTutorialStage();           // 下一步
UEditorTutorial::GoToPreviousTutorialStage();       // 上一步
UEditorTutorial::OpenAsset(SomeAsset);              // 打开资产
```

## Demo 示例

### 最小教程蓝图（纯数据配置）

Guided Tutorials 主要通过蓝图资产工作，不需要编写 C++ 代码。最简方式是创建 `UEditorTutorial` 的蓝图子类并配置属性。

如果需要在 C++ 中注册自定义教程上下文：

```cpp
// MyTutorialModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "IntroTutorials"  // 依赖教程模块
});
```

```cpp
// MyTutorialHelper.h
#pragma once
#include "IIntroTutorials.h"

class FMyTutorialHelper
{
public:
    static void RegisterTutorials()
    {
        if (IIntroTutorials::IsAvailable())
        {
            IIntroTutorials& Tutorials = IIntroTutorials::Get();
            
            FTutorialCategory Category;
            Category.Identifier = TEXT("MyPlugin");
            Category.Title = NSLOCTEXT("MyPlugin", "Tutorials", "My Plugin Tutorials");
            Tutorials.RegisterCategory(Category);
        }
    }
};
```

## 模块依赖

### Public 依赖（使用者需要引用）

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `InputCore` | 输入系统 |
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心 |
| `Documentation` | 文档系统集成 |
| `GraphEditor` | 图形编辑器支持 |
| `BlueprintGraph` | 蓝图图表支持 |
| `MessageLog` | 消息日志 |
| `ApplicationCore` | 应用核心 |

### 私有依赖（内部使用）

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器框架 |
| `Kismet` | 蓝图编辑器集成 |
| `ContentBrowser` | 内容浏览器集成 |
| `LevelEditor` | 关卡编辑器集成 |
| `PropertyEditor` | 属性面板定制 |
| `AssetTools` | 资产工具注册 |
| `ToolMenus` | 菜单系统扩展 |
| `Settings` | 设置面板注册 |
| `Analytics` | 分析事件 |

## 维护状态

### 近期更新

| 日期 | Hash | 提交信息 | 解读 |
|---|---|---|---|
| 2025-05-21 | `269aeb1` | Replaced bool arguments with EFindObjectFlags. | API 清理：将 `StaticFindObject` 的布尔参数替换为枚举标志，跟随引擎 API 演进 |
| 2025-03-13 | `b059f7b` | Fix trivial unreachable code warnings. | 编译警告修复 |
| 2024-06-27 | `a890c0c` | Fixed some 'deprecated' FString usage. | 修复废弃的 FString 用法，代码维护 |

### 维护评价

- **创建时间**：2022 年 2 月，随 UE5 首版发布
- **最近更新**：最近一次功能性更新（`FindObjectFlags` 替换）在 2025 年 5 月，但属于 API 适配而非新功能
- **维护状态**：**维护不活跃**。近 3 年的提交全部是编译警告修复和 API 适配，没有新功能开发
- **已知限制**：
  - 默认禁用（`Installed: false`），需要手动启用
  - UE5 的内置教程已逐步迁移到其他方式（如 UDN 文档系统）
  - `bDisableTutorials` 默认为 `true`，暗示 Epic 可能在逐步淡化此系统
- **推荐**：如果你需要为项目创建交互式编辑器教程，这个框架仍然可用且功能完整。但要注意它不被默认启用，未来可能会被替代方案取代。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/GuidedTutorials)
- 官方文档：无（.uplugin 中 DocsURL 为空）
