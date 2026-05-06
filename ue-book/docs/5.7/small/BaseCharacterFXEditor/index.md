# BaseCharacterFXEditor

> Base classes for character FX asset editors

| 属性 | 值 |
|---|---|
| 中文名 | 角色FX编辑器基类 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产预览场景、工具箱基类） |
| 模块 | `BaseCharacterFXEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-31 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CharacterFXEditor/BaseCharacterFXEditor) | |

## 用途

该插件提供了创建角色模拟资产编辑器（如布料、毛发、肌肉等）所需的基础类和框架。它基于 UE 的 UAssetEditor 和 Interactive Tools Framework 搭建，将业务逻辑分散在以下几个层面：

- **Editor 类**（`UBaseCharacterFXEditor`）：负责管理输入的资产对象和启动编辑器。
- **Toolkit 类**（`FBaseCharacterFXEditorToolkit`）：负责 UI 管理，包括视口、工具栏、布局等。
- **Mode 类**（`UBaseCharacterFXEditorMode`）：存储工具间共享状态（如 ToolTargets），并注册工具和目标工厂。
- **ModeToolkit 类**（`FBaseCharacterFXEditorModeToolkit`）：负责编辑器侧边栏的工具属性面板、工具按钮、通知等。

开发者只需继承这些基类，实现少量纯虚函数即可快速搭建一个完整的 CharacterFX 专用资产编辑器，避免重复编写编辑器基础设施代码。

## 使用场景

- 你需要开发一个用于编辑布料模拟资产（如 UClothingAsset）的编辑器，希望复用交互工具框架和视口管理。
- 你有一个自定义的毛发模拟数据资产，需要为它提供一个专用的 3D 编辑器，支持网格操作和实时预览。
- 你希望快速创建一个与现有建模工具集（MeshModelingToolset）兼容的编辑器，以便让工具直接操作你的资产。

## 蓝图用法

由于本插件的所有核心类均标记为 `Abstract`、`MinimalAPI` 或纯 C++ 类，未暴露任何 `BlueprintCallable` 函数或可蓝图的属性，因此**无公开蓝图 API**。所有编辑器逻辑必须在 C++ 中通过继承实现。

## C++ 用法

### 头文件引入

```cpp
#include "BaseCharacterFXEditor.h"
#include "BaseCharacterFXEditorToolkit.h"
#include "BaseCharacterFXEditorMode.h"
#include "BaseCharacterFXEditorModeToolkit.h"
```

### 基本用法

创建一个具体的 CharacterFX 编辑器，需要实现以下三个子类（示例以 ClothEditor 为例）：

#### 1. 继承 UBaseCharacterFXEditor

```cpp
// MyClothEditor.h
#pragma once
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

```cpp
// MyClothEditor.cpp
#include "MyClothEditor.h"
#include "MyClothEditorToolkit.h"

TSharedPtr<FBaseAssetToolkit> UMyClothEditor::CreateToolkit()
{
    return MakeShared<FMyClothEditorToolkit>(this, "MyClothEditor");
}
```

#### 2. 继承 FBaseCharacterFXEditorToolkit

```cpp
// MyClothEditorToolkit.h
#pragma once
#include "BaseCharacterFXEditorToolkit.h"

class FMyClothEditorToolkit : public FBaseCharacterFXEditorToolkit
{
public:
    FMyClothEditorToolkit(UAssetEditor* InOwningAssetEditor, const FName& ModuleName)
        : FBaseCharacterFXEditorToolkit(InOwningAssetEditor, ModuleName) {}

protected:
    virtual FEditorModeID GetEditorModeId() const override
    {
        return TEXT("EM_MyClothEditorMode");
    }
    virtual void PostInitAssetEditor() override
    {
        FBaseCharacterFXEditorToolkit::PostInitAssetEditor();
        // 可在这里创建自定义 UI 元素
    }
};
```

#### 3. 继承 UBaseCharacterFXEditorMode

```cpp
// MyClothEditorMode.h
#pragma once
#include "BaseCharacterFXEditorMode.h"
#include "MyClothEditorMode.generated.h"

UCLASS()
class UMyClothEditorMode : public UBaseCharacterFXEditorMode
{
    GENERATED_BODY()
public:
    virtual void AddToolTargetFactories() override;
    virtual void RegisterTools() override;
    virtual void CreateToolTargets(const TArray<TObjectPtr<UObject>>& AssetsIn) override;
};
```

```cpp
// MyClothEditorMode.cpp
#include "MyClothEditorMode.h"
#include "ToolTargets/DynamicMeshComponentToolTarget.h"
#include "Tools/BaseSkeletalMeshTool.h"

void UMyClothEditorMode::AddToolTargetFactories()
{
    UDynamicMeshComponentToolTargetFactory* Factory = NewObject<UDynamicMeshComponentToolTargetFactory>();
    AddToolTargetFactory(Factory);
}

void UMyClothEditorMode::RegisterTools()
{
    UBaseSkeletalMeshTool* Tool = NewObject<UBaseSkeletalMeshTool>();
    Tool->SetToolDisplayName(LOCTEXT("MyTool", "My Tool"));
    AddTool(Tool);
}

void UMyClothEditorMode::CreateToolTargets(const TArray<TObjectPtr<UObject>>& AssetsIn)
{
    for (UObject* Asset : AssetsIn)
    {
        // 为每个资产创建一个 ToolTarget，例如包裹一个 UDynamicMeshComponent
        UToolTarget* Target = MakeDynamicMeshToolTargetForAsset(Asset);
        if (Target)
        {
            ToolTargets.Add(Target);
        }
    }
}
```

#### 4. 注册模块

```cpp
// MyClothEditorModule.cpp
#include "MyClothEditorModule.h"
#include "MyClothEditor.h"

IMPLEMENT_MODULE(FMyClothEditorModule, MyClothEditor);

void FMyClothEditorModule::StartupModule()
{
    // 注册资产编辑器
    IAssetEditorModule& AssetEditorModule = FModuleManager::LoadModuleChecked<IAssetEditorModule>("AssetEditor");
    AssetEditorModule.RegisterEditorForAsset(UMyClothAsset::StaticClass(), CreateAssetEditorInstance<UMyClothEditor>);
}
```

## Demo 示例

以下是一个最小的、可编译的示例，展示如何创建一个空的 CharacterFX 编辑器。该示例不包含具体工具，仅演示框架搭建流程。

### MyEmptyEditor.h

```cpp
#pragma once
#include "BaseCharacterFXEditor.h"
#include "MyEmptyEditor.generated.h"

UCLASS()
class UMyEmptyEditor : public UBaseCharacterFXEditor
{
    GENERATED_BODY()
public:
    virtual TSharedPtr<FBaseAssetToolkit> CreateToolkit() override;
};
```

### MyEmptyEditor.cpp

```cpp
#include "MyEmptyEditor.h"
#include "BaseCharacterFXEditorToolkit.h"

class FMyEmptyEditorToolkit : public FBaseCharacterFXEditorToolkit
{
public:
    FMyEmptyEditorToolkit(UAssetEditor* InOwningAssetEditor)
        : FBaseCharacterFXEditorToolkit(InOwningAssetEditor, "MyEmptyEditor") {}
protected:
    virtual FEditorModeID GetEditorModeId() const override { return TEXT("EM_MyEmptyEditorMode"); }
};

TSharedPtr<FBaseAssetToolkit> UMyEmptyEditor::CreateToolkit()
{
    return MakeShared<FMyEmptyEditorToolkit>(this);
}
```

### MyEmptyEditorMode.h

```cpp
#pragma once
#include "BaseCharacterFXEditorMode.h"
#include "MyEmptyEditorMode.generated.h"

UCLASS()
class UMyEmptyEditorMode : public UBaseCharacterFXEditorMode
{
    GENERATED_BODY()
public:
    virtual void AddToolTargetFactories() override {}
    virtual void RegisterTools() override {}
    virtual void CreateToolTargets(const TArray<TObjectPtr<UObject>>& AssetsIn) override {}
};
```

### MyEmptyEditorMode.cpp

```cpp
#include "MyEmptyEditorMode.h"

// 所有纯虚函数已实现为空，模式可正常初始化
```

### MyEmptyEditorModule.cpp

```cpp
#include "Modules/ModuleManager.h"

IMPLEMENT_MODULE(FDefaultModuleImpl, MyEmptyEditor);
```

注意：实际使用时需要注册对应的资产类型并提供资产工厂。

## 模块依赖

| 模块 / 插件 | 用途 |
|---|---|
| `GeometryProcessing` | 提供动态网格组件（UDynamicMeshComponent）和几何处理工具 |
| `MeshModelingToolset` | 提供交互式建模工具框架（Interactive Tools Framework） |
| `EditorInteractiveToolsFramework` | 编辑器交互工具框架（UEdMode、UInteractiveToolManager 等） |
| `AssetEditor` | 资产编辑器基础设施（UAssetEditor、FBaseAssetToolkit 等） |

其他常见模块（如 CoreUObject、Engine、Slate、UnrealEd 等）为标准依赖，此处省略。

## 维护状态

### 近期更新

- 2025-07-11 `1bb7cec8` 移除 TSubclassOf<T> 的空初始化器
- 2025-07-10 `9803c443` 添加 UE_INLINE_GENERATED_CPP_BY_NAME 宏
- 2025-06-25 `1cbb35d8` 修复 Dataflow Editor 中视口关闭时的悬空指针问题
- 2025-05-31 `c5b82d05` 更新 DLL 存储宏位置
- 2025-05-31 `52e3dac1` 首次提交，基础框架

### 维护评价

该插件创建于 2025 年 5 月，距今约 4 个月，属于非常年轻的实验性插件。从提交记录看，开发团队在持续更新（最近一次更新在 2025-07-11），主要涉及代码规范化、编译修复和 Bug 修复。虽然版本号为 0.1，但框架基础已经稳定。目前实验性标记意味着 API 可能发生变动，但推荐需要自定义 CharacterFX 编辑器的开发者基于此框架进行开发。

## 相关链接

- [源码（主分支）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CharacterFXEditor/BaseCharacterFXEditor)
- [官方文档](https://docs.unrealengine.com/5.3/en-US/creating-and-editing-character-fx-assets/)（参考通用资产编辑器指南）
- [测试用例示例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CharacterFXEditor)（同一目录下的其他插件如 ClothEditor 可作参考）