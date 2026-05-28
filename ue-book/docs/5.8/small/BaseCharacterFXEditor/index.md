# BaseCharacterFXEditor

> Base classes for character FX asset editors

| 属性 | 值 |
|---|---|
| 中文名 | 角色FX编辑器基类 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BaseCharacterFXEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-06 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CharacterFXEditor/BaseCharacterFXEditor) | |

## 用途

BaseCharacterFXEditor 是一个提供角色特效（Character FX）资产编辑器基础框架的实验性插件。它并非用于直接创建具体的编辑器，而是作为基类，为开发自定义的角色模拟资产（如布料、毛发、皮肤等）编辑器提供标准化的基础设施。

它解决了创建此类编辑器时的重复性工作问题，提供了：
1.  编辑器模式（Editor Mode）和工具包（Toolkit）的标准化初始化和管理。
2.  与 UE5 交互式工具框架（Interactive Tools Framework）的集成。
3.  视口（Viewport）、工具面板（Tool Palette）和属性面板（Details View）的通用布局和控件。
4.  接受/取消（Accept/Cancel）工具操作的统一命令和 UI 支持。

通过继承此插件中的基类，开发者可以专注于特定资产类型（如布料）的业务逻辑和工具实现，而无需从零开始搭建编辑器 UI 和模式管理。

## 使用场景

-   **你正在为 UE5 开发一个自定义的布料模拟资产编辑器** → 请继承 `UBaseCharacterFXEditor`、`UBaseCharacterFXEditorMode` 和 `FBaseCharacterFXEditorToolkit`，专注于实现布料特有的工具和网格目标。
-   **你需要创建一个具有标准工具栏、视口和接受/取消按钮的专用资产编辑器** → BaseCharacterFXEditor 提供的框架正是为此类需求设计。

## 蓝图用法

此插件主要为 C++ 框架，公开的蓝图可调用函数较少，主要用于编辑器内部状态查询和交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetActiveToolDisplayName` | 获取当前激活工具的显示名称 | `FBaseCharacterFXEditorModeToolkit` |
| `GetToolPaletteNames` | 获取编辑器工具栏中的工具面板类别名称 | `FBaseCharacterFXEditorModeToolkit` |
| `GetToolPaletteDisplayName` | 获取特定工具面板类别的人类可读名称 | `FBaseCharacterFXEditorModeToolkit` |
| `PostNotification` | 在工具包中设置通知消息 | `FBaseCharacterFXEditorModeToolkit` |
| `ClearNotification` | 清除工具包中的通知消息 | `FBaseCharacterFXEditorModeToolkit` |
| `PostWarning` | 在工具包中设置警告消息 | `FBaseCharacterFXEditorModeToolkit` |
| `ClearWarning` | 清除工具包中的警告消息 | `FBaseCharacterFXEditorModeToolkit` |

**使用示例（蓝图描述）**
在你的具体编辑器子类（如 `FMyClothEditorModeToolkit`）中，你可能会在工具事件（如 `OnToolStarted`）中调用 `PostWarning` 来向用户显示工具使用注意事项，并在工具结束时调用 `ClearWarning`。

## C++ 用法

此插件的用法主要体现在 C++ 继承和覆盖上。

### 头文件引入

```cpp
#include "BaseCharacterFXEditor.h"
#include "BaseCharacterFXEditorMode.h"
#include "BaseCharacterFXEditorToolkit.h"
```

### 基本用法

要创建一个自定义的资产编辑器，你需要继承三个主要的基类。

1.  **继承编辑器主类** (`UBaseCharacterFXEditor`)：
    *来源: `Source/BaseCharacterFXEditor/Public/BaseCharacterFXEditor.h`*

```cpp
// MyClothEditor.h
#include "BaseCharacterFXEditor.h"

class UMyClothEditor : public UBaseCharacterFXEditor
{
    GENERATED_BODY()

public:
    // 必须实现的纯虚函数，用于创建你自定义的工具包
    virtual TSharedPtr<FBaseAssetToolkit> CreateToolkit() override;
};
```

2.  **继承编辑器模式** (`UBaseCharacterFXEditorMode`)：
    *来源: `Source/BaseCharacterFXEditor/Public/BaseCharacterFXEditorMode.h`*

```cpp
// MyClothEditorMode.h
#include "BaseCharacterFXEditorMode.h"

class UMyClothEditorMode : public UBaseCharacterFXEditorMode
{
    GENERATED_BODY()

public:
    // 必须实现的纯虚函数，用于注册自定义工具
    virtual void RegisterTools() override;
    // 必须实现的纯虚函数，用于创建工具目标（如从资产生成动态网格）
    virtual void CreateToolTargets(const TArray<TObjectPtr<UObject>>& AssetsIn) override;
    // 可选：添加工具目标工厂
    virtual void AddToolTargetFactories() override;
};
```

3.  **继承编辑器工具包** (`FBaseCharacterFXEditorToolkit`)：
    *来源: `Source/BaseCharacterFXEditor/Public/BaseCharacterFXEditorToolkit.h`*

```cpp
// MyClothEditorToolkit.h
#include "BaseCharacterFXEditorToolkit.h"

class FMyClothEditorToolkit : public FBaseCharacterFXEditorToolkit
{
public:
    FMyClothEditorToolkit(UAssetEditor* InOwningAssetEditor, const FName& ModuleName);

    // 必须实现的纯虚函数，返回你自定义编辑器模式的 ID
    virtual FEditorModeID GetEditorModeId() const override;
    // 可选：覆盖以提供自定义视口客户端
    virtual TSharedPtr<FEditorViewportClient> CreateEditorViewportClient() const override;
};
```

### 进阶用法

在实现了上述基类后，你需要将它们连接起来。在你的编辑器模式中注册自定义工具，并在工具包中初始化它。

*来源: 结合 `BaseCharacterFXEditorMode.h` 和 `BaseCharacterFXEditorToolkit.h` 的设计理念*

```cpp
// MyClothEditorMode.cpp
void UMyClothEditorMode::RegisterTools()
{
    // 使用 UInteractiveToolManager 注册你的自定义工具，例如一个“平滑”工具
    UInteractiveToolManager* ToolManager = GetToolManager();
    // ... (使用 RegisterToolType 注册工具)
}

void UMyClothEditorMode::CreateToolTargets(const TArray<TObjectPtr<UObject>>& AssetsIn)
{
    // 为每个传入的资产（如 UClothAsset）创建对应的 ToolTarget（如 UClothToolTarget）
    for (UObject* Asset : AssetsIn)
    {
        if (UClothAsset* ClothAsset = Cast<UClothAsset>(Asset))
        {
            // 创建 ToolTarget 并将其添加到 ToolTargets 数组
            UClothToolTarget* Target = NewObject<UClothToolTarget>(this);
            Target->SetAsset(ClothAsset);
            ToolTargets.Add(Target);
        }
    }
}

// MyClothEditorToolkit.cpp
void FMyClothEditorToolkit::PostInitAssetEditor()
{
    // 调用基类初始化
    FBaseCharacterFXEditorToolkit::PostInitAssetEditor();
    // 可以在此处为你的自定义模式提供额外数据
    if (UBaseCharacterFXEditorMode* Mode = GetEditorMode())
    {
        // InitializeEdMode(Mode); // 如果需要传递特定数据
    }
}
```

## Demo 示例

一个最小的、可编译的自定义布料编辑器实现骨架。

**MyClothEditor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "BaseCharacterFXEditor.h"
#include "MyClothEditor.generated.h"

UCLASS()
class UMyClothEditor : public UBaseCharacterFXEditor
{
	GENERATED_BODY()

public:
	virtual TSharedPtr<FBaseAssetToolkit> CreateToolkit() override;
};
```

**MyClothEditorMode.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "BaseCharacterFXEditorMode.h"
#include "MyClothEditorMode.generated.h"

UCLASS()
class UMyClothEditorMode : public UBaseCharacterFXEditorMode
{
	GENERATED_BODY()

public:
	virtual void RegisterTools() override;
	virtual void CreateToolTargets(const TArray<TObjectPtr<UObject>>& AssetsIn) override;
	virtual void AddToolTargetFactories() override;
};
```

**MyClothEditorToolkit.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "BaseCharacterFXEditorToolkit.h"

class UMyClothEditorToolkit : public FBaseCharacterFXEditorToolkit
{
public:
	UMyClothEditorToolkit(UAssetEditor* InOwningAssetEditor, const FName& ModuleName);
	virtual FEditorModeID GetEditorModeId() const override;
};
```

**MyClothEditor.cpp**
```cpp
#include "MyClothEditor.h"
#include "MyClothEditorToolkit.h"

TSharedPtr<FBaseAssetToolkit> UMyClothEditor::CreateToolkit()
{
	return MakeShareable(new UMyClothEditorToolkit(this, TEXT("MyClothEditorModule")));
}
```

## 模块依赖

从 `.uplugin` 的 `Plugins` 部分提取。要使用此插件及其基础，你的项目可能需要依赖这些模块。

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 几何处理功能，被 BaseCharacterFXEditor 依赖 |
| `MeshModelingToolset` | 网格建模工具集，被 BaseCharacterFXEditor 依赖 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-07-11 | `1bb7cec8` | Ran update script to removed null initializers when creating TSubclassOf<T> since it will use a code | 移除了 TSubclassOf 初始化时的空初始值 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 为源文件添加了 UE_INLINE_GENERATED_CPP_BY_NAME 宏 |
| 2025-06-25 | `1cbb35d8` | Dataflow Editor - Fixed dangling pointers issue with viewports closing order. | 修复了 Dataflow Editor 中因视口关闭顺序导致的悬空指针问题 |
| 2025-05-31 | `c5b82d05` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 使用 UnrealCodeFixup 更新了头文件的 DLL 导出声明 |

### 维护评价

-   **实验性插件**：`.uplugin` 明确标记为 `IsExperimentalVersion: true`，且 `Installed: false`，表明这是一个实验性功能，尚未准备好用于生产环境。
-   **活跃维护**：最近的提交（2025年7月）表明该插件仍在被维护，但主要是底层代码修复和编译兼容性更新，而非功能增强。
-   **主要用途**：作为其他角色 FX 编辑器（如 Chaos Cloth Editor）的基础，自身并非最终用户产品。
-   **推荐使用**：**仅建议**作为开发自定义角色模拟资产编辑器的**基础框架**。不推荐直接集成到最终项目中。由于其高度实验性和抽象性，使用者需要具备一定的 UE5 编辑器扩展开发经验。
-   **风险提示**：作为实验性插件，其 API 和结构可能在未来版本中发生 breaking changes。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CharacterFXEditor/BaseCharacterFXEditor)
-   [官方文档](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CharacterFXEditor/BaseCharacterFXEditor) (无独立文档)