# Material Asset Wizard

> Enables new factories for Materials and Material Instances.
> Requires setting Tagged Asset Browser Configuration properties under Editor Preferences -> Material Editor Settings.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MaterialAssetWizard` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/MaterialAssetWizard) | |

## 用途

该插件为 Unreal Engine 的材质编辑器提供了增强的资产创建工作流。它通过提供新的 `UFactory` 子类，替换了引擎默认的材质和材质实例创建工厂。其核心功能是：在创建新材质或材质实例时，会弹出一个“标记资产浏览器”（Tagged Asset Browser）窗口，允许用户从现有资产库中选择一个基础材质（Base Material）作为新资产的起点。这解决了默认工厂只能创建空白材质的问题，极大地提高了基于现有材质进行迭代和派生的工作效率，尤其适用于需要大量创建材质变体的美术和 TA 工作流。

## 使用场景

- 你是一名技术美术（TA），需要为一个角色快速创建一套基于同一主材质（Master Material）的材质实例（Material Instance），用于控制不同部位的颜色、粗糙度等参数。
- 你是一名环境美术，需要创建多个相似的材质（如不同种类的木头、石头），希望它们都基于一个通用的、已优化的基础材质，以确保渲染性能和风格统一。
- 你希望利用项目中已有的、经过验证的材质资产，避免从零开始创建，从而提升资产制作的一致性和效率。

## 蓝图用法

该插件主要通过编辑器集成工作，不直接暴露蓝图可调用的函数节点。其功能通过重写 `UFactory` 的 `ConfigureProperties` 方法实现，在用户通过内容浏览器右键菜单选择“材质”或“材质实例”时自动触发。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ConfigureProperties` | （重写）在创建资产前弹出标记资产浏览器窗口，用于选择基础材质。 | `UMaterialFactoryWithAssetWizardBase` |
| `FactoryCreateNew` | （重写）根据用户在向导中选择的基础材质（或无选择）来创建最终的材质或材质实例资产。 | `UMaterialFactoryWithAssetWizard`, `UMaterialInstanceConstantFactoryWithAssetWizard` |

### 使用示例（蓝图描述）

1.  在内容浏览器中，右键点击空白处。
2.  在“创建高级资产”或“材质”菜单下，选择“材质”或“材质实例”。
3.  此时会弹出一个名为“选择基础材质”或类似标题的窗口（由 `WindowTitle` 属性控制）。
4.  该窗口内嵌了标记资产浏览器，你可以浏览、搜索并选择一个现有的材质资产。
5.  点击“确定”或双击选中的资产，即可基于该材质创建一个新的材质或材质实例。如果不选择任何资产，则创建一个空白材质。

## C++ 用法

### 头文件引入

```cpp
#include "MaterialFactoryWithAssetWizard.h"
```

### 基本用法

该插件的核心是提供两个具体的工厂类。通常不需要直接实例化它们，它们由引擎的资产创建系统自动使用。但理解其结构有助于扩展。

```cpp
// 来自 Source/MaterialAssetWizard/Public/MaterialFactoryWithAssetWizard.h
// UMaterialFactoryWithAssetWizard 和 UMaterialInstanceConstantFactoryWithAssetWizard
// 是最终用户会用到的两个工厂类。
// 它们继承自 UMaterialFactoryWithAssetWizardBase，并实现了具体的资产创建逻辑。

// 示例：在自定义工具中强制使用此工厂创建材质（非典型用法）
UMaterialFactoryWithAssetWizard* Factory = NewObject<UMaterialFactoryWithAssetWizard>();
// 配置工厂属性（通常由编辑器自动调用 ConfigureProperties）
// Factory->ConfigureProperties(); // 这会弹出UI窗口
// 创建资产（需要提供完整的参数）
// UObject* NewMaterial = Factory->FactoryCreateNew(UMaterial::StaticClass(), SomeOuter, TEXT("NewMaterial"), RF_NoFlags, nullptr, GWarn);
```

### 进阶用法

插件支持异步工厂工作流（`ConfigurePropertiesAsync`），这是 UE5 中用于避免阻塞编辑器线程的现代模式。你可以参考其实现来为自己的资产工厂添加异步支持。

```cpp
// 来自 Source/MaterialAssetWizard/Public/MaterialFactoryWithAssetWizard.h
// UMaterialFactoryWithAssetWizardBase 重写了 ConfigurePropertiesAsync。
// 当编辑器以异步模式请求配置时，会调用此方法。
// 它内部会创建并显示一个 SWindow，等待用户交互完成后再通过 OnComplete 回调返回结果。
virtual bool ConfigurePropertiesAsync(FOnFactoryConfigurePropertiesAsyncComplete OnComplete, FOnFactoryConfigurePropertiesAsyncCancelled OnCancelled) override;
```

## Demo 示例

以下示例展示如何创建一个自定义的材质工厂，它继承自插件提供的基类，并重写了窗口标题和空选择提示信息。

```cpp
// MyCustomMaterialFactory.h
#pragma once

#include "CoreMinimal.h"
#include "MaterialFactoryWithAssetWizard.h"
#include "MyCustomMaterialFactory.generated.h"

UCLASS()
class UMyCustomMaterialFactory : public UMaterialFactoryWithAssetWizardBase
{
	GENERATED_BODY()

public:
	UMyCustomMaterialFactory()
	{
		// 自定义向导窗口的标题
		WindowTitle = NSLOCTEXT("MyPlugin", "CustomMatFactoryTitle", "选择基础材质（自定义）");
		// 自定义未选择任何资产时的提示信息
		EmptySelectionMessage = NSLOCTEXT("MyPlugin", "CustomMatFactoryEmpty", "未选择基础材质，将创建空白材质。");
		// 可以在此设置 ConfigurationPath 指向特定的标记资产浏览器配置资产
		// ConfigurationPath = FSoftObjectPath(TEXT("/Game/Config/MyTaggedAssetBrowserConfig.MyTaggedAssetBrowserConfig"));
	}

	// 重写工厂创建逻辑，这里简单调用父类实现
	virtual UObject* FactoryCreateNew(UClass* Class, UObject* InParent, FName Name, EObjectFlags Flags, UObject* Context, FFeedbackContext* Warn) override
	{
		// 此处可以添加自定义逻辑，例如在创建前验证 BaseMaterial
		return Super::FactoryCreateNew(Class, InParent, Name, Flags, Context, Warn);
	}

	// 确保此工厂出现在“新建资产”菜单中
	virtual bool ShouldShowInNewMenu() const override { return true; }
};
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

- 2026-02-04 `0a79374b` 重写了插件描述
- 2025-12-08 `b0e8a065` 确保在创建新材质资产时编译材质资源和着色器，使其缩略图正确渲染
- 2025-10-29 `b8f9bca5` 修复了材质异步向导工厂的问题
- 2025-10-24 `4e7de009` 为 Niagara 和材质向导启用了异步工厂工作流
- 2025-10-24 `08821bf2` 为标记资产浏览器窗口添加了异步支持

### 维护评价

该插件近期有持续的更新记录，时间跨度约四个月，提交内容涵盖功能增强、异步支持添加及问题修复。这表明插件处于活跃维护状态，开发者正在积极优化其功能和稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/MaterialAssetWizard)
- [测试用例]（未在提供的源码路径中找到独立的测试文件，可能集成在引擎的自动化测试中）