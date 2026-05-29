# Project Launcher

> Configure custom project launch profiles.

| 属性 | 值 |
|---|---|
| 中文名 | 项目启动器 |
| 分类 | Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ProjectLauncher` (Editor), `CommonLaunchExtensions` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/ProjectLauncher) | |

## 用途

Project Launcher 是 Unreal Frontend (UFE) 中的自定义启动配置系统。它提供了一个可扩展的框架，用于管理、配置和执行复杂的项目启动工作流。其核心是解决多平台、多目标（构建、烹饪、同步、部署、测试等）场景下的启动配置问题。它允许开发者通过“扩展”机制添加自定义步骤（如特定内容烹饪选项、构建同步、UGS 集成等），并将这些步骤的配置以树状 UI 展示，最终生成和执行 UAT 命令。本质上，它是 UFE 中“启动”按钮背后的强大引擎。

## 使用场景

- 你需要为不同的目标平台（Win64, Linux, Mac, 主机等）创建独立的启动配置，并保存为可复用的“配置文件”。
- 你的项目有复杂的烹饪需求，例如：只烹饪特定地图、选择特定文化本地化文件、或使用高级烹饪选项。
- 你需要从内部构建服务器（如 Zen Build Service）同步特定的构建版本到本地进行测试。
- 你希望集成 Unreal Insights 进行性能分析，并在启动时自动配置追踪通道。
- 你的工作流涉及自定义 UAT 命令或参数，需要通过 UI 进行配置。
- 你需要一个统一的界面来管理所有与构建、部署和测试相关的启动前步骤。

## 蓝图用法

Project Launcher 是一个编辑器（Editor）插件，主要提供 UFE 中的 UI 界面。它不包含可在游戏逻辑中使用的蓝图节点（BlueprintCallable）。其扩展和配置主要通过 C++ 继承其基类来实现。

## C++ 用法

Project Launcher 的主要用途是通过继承其提供的基类来创建自定义的启动扩展（Launch Extensions）。

### 头文件引入

```cpp
#include "ProjectLauncher.h" // 核心基类和模型
#include "CommonLaunchExtensions.h" // 通用扩展基类（如 FBuildCookRunCommandExtension）
```

### 基本用法：创建自定义启动扩展

要添加一个新的启动选项（如“我的自定义步骤”），你需要继承 `ProjectLauncher::FLaunchExtension` 并重写其虚函数。

**文件：`MyCustomLaunchExtension.h`**
```cpp
#pragma once

#include "ProjectLauncher.h"

class FMyCustomLaunchExtensionInstance : public ProjectLauncher::FLaunchExtensionInstance
{
public:
    FMyCustomLaunchExtensionInstance(FArgs& InArgs) : FLaunchExtensionInstance(InArgs) {}
    virtual ~FMyCustomLaunchExtensionInstance() = default;

    // 重写此函数以在启动配置树中添加自定义 UI 节点
    virtual void CustomizeTree(ProjectLauncher::FLaunchProfileTreeData& ProfileTreeData) override
    {
        // 在树中添加一个复选框或下拉框等
        ProfileTreeData.TreeItems.Add(
            MakeShared<ProjectLauncher::FLaunchProfileTreeNode>(
                FText::FromString(TEXT("启用我的功能")),
                GetShared(),
                [](TSharedRef<FLaunchExtensionInstance> InInstance) -> TSharedRef<SWidget>
                {
                    // 返回一个 SCheckBox 或其他 Slate 控件
                    return SNew(SCheckBox);
                }
            )
        );
    }

    // 重写此函数以修改最终的 UAT 命令行
    virtual void CustomizeUATCommandLine(FString& InOutCommandLine) override
    {
        // 根据 UI 状态向命令行添加参数
        InOutCommandLine += TEXT(" -MyCustomOption");
    }
};

class FMyCustomLaunchExtension : public ProjectLauncher::FLaunchExtension
{
public:
    // 为每个配置文件创建实例
    virtual TSharedPtr<ProjectLauncher::FLaunchExtensionInstance> CreateInstanceForProfile(ProjectLauncher::FLaunchExtensionInstance::FArgs& InArgs) override
    {
        return MakeShared<FMyCustomLaunchExtensionInstance>(InArgs);
    }

    // 内部名称，用于标识和序列化
    virtual const TCHAR* GetInternalName() const override { return TEXT("MyCustomExtension"); }

    // 在 UFE 中显示的友好名称
    virtual FText GetDisplayName() const override { return FText::FromString(TEXT("我的自定义扩展")); }

    // 是否默认为此配置文件创建此扩展实例
    virtual bool IsCreatedByDefault(ILauncherProfileRef InProfile, TSharedRef<ProjectLauncher::FModel> InModel) const override { return true; }
};
```

### 进阶用法：基于构建烹饪运行命令扩展

许多扩展与“构建、烹饪、运行”（BuildCookRun）过程相关。`CommonLaunchExtensions` 模块提供了 `FBuildCookRunCommandExtension` 基类，它简化了针对此流程的扩展开发。

```cpp
#include "CommonLaunchExtensions.h" // 包含 FBuildCookRunCommandExtension

class FMyCookExtension : public ProjectLauncher::FBuildCookRunCommandExtension
{
public:
    virtual TSharedPtr<ProjectLauncher::FLaunchExtensionInstance> CreateInstanceForProfile(ProjectLauncher::FLaunchExtensionInstance::FArgs& InArgs) override;
    virtual const TCHAR* GetInternalName() const override { return TEXT("MyCookExtension"); }
    virtual FText GetDisplayName() const override { return FText::FromString(TEXT("我的烹饪扩展")); }
};
```

对应的 `Instance` 类需要继承 `FBuildCookRunCommandExtensionInstance`，并可以重写 `CustomizeTree` 和 `CustomizeUATCommandLine` 来影响烹饪过程。

## Demo 示例

以下是一个最小的自定义启动扩展，它在启动命令行中添加一个参数。

**文件：`SimpleParamExtension.h`**
```cpp
#pragma once

#include "ProjectLauncher.h"

class FSimpleParamExtensionInstance : public ProjectLauncher::FLaunchExtensionInstance
{
public:
    FSimpleParamExtensionInstance(FArgs& InArgs) : FLaunchExtensionInstance(InArgs) {}
    virtual void CustomizeUATCommandLine(FString& InOutCommandLine) override
    {
        InOutCommandLine += TEXT(" -EnableSimpleFeature");
    }
};

class FSimpleParamExtension : public ProjectLauncher::FLaunchExtension
{
public:
    virtual TSharedPtr<ProjectLauncher::FLaunchExtensionInstance> CreateInstanceForProfile(ProjectLauncher::FLaunchExtensionInstance::FArgs& InArgs) override
    {
        return MakeShared<FSimpleParamExtensionInstance>(InArgs);
    }
    virtual const TCHAR* GetInternalName() const override { return TEXT("SimpleParam"); }
    virtual FText GetDisplayName() const override { return FText::FromString(TEXT("简单参数")); }
    virtual bool IsCreatedByDefault(ILauncherProfileRef InProfile, TSharedRef<ProjectLauncher::FModel> InModel) const override { return true; }
};
```

要将此扩展注册到系统，你需要在你的插件或模块的 `StartupModule` 中将其添加到 `ProjectLauncher::FModel`。

**文件：`MyProjectLauncherExtensions.cpp`**
```cpp
#include "MyProjectLauncherExtensions.h"
#include "ProjectLauncher.h"

void FMyProjectLauncherExtensionsModule::StartupModule()
{
    // 获取 Project Launcher 的模型并注册扩展
    auto Model = ProjectLauncher::FModel::Get();
    if (Model.IsValid())
    {
        Model->RegisterExtension(MakeShared<FSimpleParamExtension>());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RuntimeMeshComponent` | 为高级烹饪扩展提供网格体相关的功能（可能用于预览等） |
| `NavigationSystem` | 为某些启动流程可能涉及的导航功能提供支持 |
| `Zen` | 用于与 Zen 构建服务（Build Service）通信，获取构建信息 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `4225c8f8` | Remove the restriction from Project Launcher that prevents package & deploy to be specified together | 移除了打包和部署不能同时指定的限制 |
| 2026-04-27 | `77966850` | Launcher2: Use the value of bUseZenStore from ProjectSettings when deciding whether to pass -ZenStor | 启动器现在使用项目设置中的 `bUseZenStore` 值来决定是否传递 `-ZenStore` 参数 |
| 2026-04-17 | `921928f4` | Add support for skipping content when downloading staged build via Project Launcher 2 Build Sync ext | 通过构建同步扩展下载暂存版本时，新增了跳过特定内容的支持 |
| 2026-04-16 | `9870b120` | Declare that several Developer modules only support desktop platforms | 声明多个开发者模块仅支持桌面平台 |
| 2026-04-14 | `c58ad33c` | Project Launcher now allows you to select maps that are in plugins. | 项目启动器现在允许你选择插件中的地图 |

### 维护评价

- **活跃维护**：该插件创建于2025年4月，属于较新的功能。从提交历史看，直至2026年5月仍有持续的功能性更新和优化。
- **实验性标记**：`.uplugin` 中 `IsBetaVersion=true`，表明其 API 和功能仍可能发生变化。
- **功能丰富**：它不是一个简单的工具，而是一个可扩展的框架，包含了构建同步、Insights集成、UGS集成等多个复杂子系统。
- **推荐使用**：**是，推荐用于编辑器工具开发**。如果你需要扩展 UFE 的启动流程，或者你的团队需要高度定制化的项目构建和部署管道，Project Launcher 是官方提供的强大基础。由于其仍处于 Beta 阶段，使用时需注意 API 的潜在变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/ProjectLauncher)
- [官方文档]() (暂无)
- [测试用例]() (暂未在提供的信息中发现)

---
*文档生成于 2025-04-24。插件仍在 Beta 阶段，请留意版本更新。*