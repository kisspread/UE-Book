# Material Designer

> Compact dynamic material creator and editor, similar in style to other DDCs.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、纹理集资产） |
| 模块 | `DynamicMaterial` (RuntimeAndProgram), `DynamicMaterialTextureSet` (RuntimeAndProgram), `DynamicMaterialEditor` (Editor), `DynamicMaterialTextureSetEditor` (Editor), `DynamicMaterialShaders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial) | |

## 用途

DynamicMaterial（Material Designer）插件提供了一个紧凑的、数据驱动的材质创建与编辑系统。它允许用户通过一个类似数据收集器（DDC）的界面，将纹理资产映射到不同的材质属性（如基础颜色、法线、金属度等），从而快速创建和编辑动态材质实例。其核心思想是将材质参数（尤其是纹理）抽象为“纹理集”（Texture Set），便于管理和复用，特别适合在虚拟制片流程中需要快速迭代和批量调整材质效果的场景。

## 使用场景

- 你在进行虚拟制片，需要为多个场景或资产快速创建和调整材质效果。
- 你希望将一组相关的纹理（如颜色、法线、粗糙度）打包成一个“纹理集”，并方便地应用到不同的材质属性上。
- 你需要一个比传统材质编辑器更简洁、专注于纹理参数配置的编辑界面。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `HasMaterialProperty` | 检查纹理集中是否定义了某个材质属性（如基础颜色）。 | `UDMTextureSet` |
| `HasMaterialTexture` | 检查纹理集中某个材质属性是否已分配了纹理。 | `UDMTextureSet` |
| `GetMaterialTexture` | 获取纹理集中某个材质属性对应的纹理和通道信息。 | `UDMTextureSet` |
| `SetMaterialTexture` | 为纹理集中的某个材质属性设置纹理和通道信息。 | `UDMTextureSet` |
| `ContainsTexture` | 检查纹理集中是否包含指定的纹理资产。 | `UDMTextureSet` |

### 使用示例（蓝图描述）

1.  **创建纹理集**：在内容浏览器中右键，选择 `Material Designer` -> `Texture Set` 来创建一个新的 `UDMTextureSet` 资产。
2.  **配置纹理集**：打开该资产，在属性面板中，你会看到一个 `Textures` 映射表。点击 `+` 添加新条目。
3.  **设置材质属性与纹理**：
    - 在 `Key` 下拉菜单中选择一个材质属性，例如 `BaseColor`。
    - 在 `Value` 中，点击 `Texture` 旁的下拉框选择一个纹理资产。
    - 在 `TextureChannel` 中选择要使用的通道（如 `RGB`）。
4.  **在材质中使用**：在材质编辑器中，你可以通过蓝图或代码获取 `UDMTextureSet` 资产，并调用 `GetMaterialTexture` 节点来获取特定属性的纹理，然后将其连接到材质节点的相应输入上。

## C++ 用法

### 头文件引入

```cpp
#include "DMTextureSet.h"
#include "DMTextureSetMaterialProperty.h"
#include "DMMaterialTexture.h"
```

### 基本用法

以下代码演示了如何创建一个 `UDMTextureSet` 对象并为其设置纹理。

```cpp
// 假设你已经有一个 UTexture* 指针 MyTexture
UTexture* MyTexture = ...;

// 创建纹理集对象
UDMTextureSet* TextureSet = NewObject<UDMTextureSet>();

// 定义要设置的材质纹理
FDMMaterialTexture MaterialTexture;
MaterialTexture.Texture = MyTexture;
MaterialTexture.TextureChannel = EDMTextureChannelMask::RGB;

// 将纹理设置到基础颜色属性上
TextureSet->SetMaterialTexture(EDMTextureSetMaterialProperty::BaseColor, MaterialTexture);

// 检查是否设置成功
if (TextureSet->HasMaterialTexture(EDMTextureSetMaterialProperty::BaseColor))
{
    FDMMaterialTexture RetrievedTexture;
    TextureSet->GetMaterialTexture(EDMTextureSetMaterialProperty::BaseColor, RetrievedTexture);
    // RetrievedTexture.Texture 现在指向 MyTexture
}
```

### 进阶用法

遍历纹理集中的所有纹理映射。

```cpp
UDMTextureSet* TextureSet = ...; // 获取或创建纹理集

const TMap<EDMTextureSetMaterialProperty, FDMMaterialTexture>& TextureMap = TextureSet->GetTextures();

for (const auto& Pair : TextureMap)
{
    EDMTextureSetMaterialProperty Property = Pair.Key;
    const FDMMaterialTexture& TextureInfo = Pair.Value;

    if (TextureInfo.Texture.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Property: %d has texture: %s"), 
            static_cast<int32>(Property), 
            *TextureInfo.Texture->GetName());
    }
}
```

## Demo 示例

**TextureSetDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "DMTextureSet.h"
#include "DMTextureSetMaterialProperty.h"
#include "DMMaterialTexture.h"

class FTextureSetDemo
{
public:
    static void RunDemo();
};
```

**TextureSetDemo.cpp**
```cpp
#include "TextureSetDemo.h"
#include "Engine/Texture2D.h"

void FTextureSetDemo::RunDemo()
{
    // 1. 创建纹理集
    UDMTextureSet* MyTextureSet = NewObject<UDMTextureSet>();

    // 2. 假设我们有一个纹理资产（实际使用中通过LoadObject或资产引用获取）
    // UTexture2D* BaseColorTexture = LoadObject<UTexture2D>(nullptr, TEXT("/Game/Textures/T_Default_BaseColor"));
    // 为了示例，这里创建一个临时纹理
    UTexture2D* BaseColorTexture = NewObject<UTexture2D>(GetTransientPackage(), NAME_None, RF_Transient);

    // 3. 配置材质纹理结构
    FDMMaterialTexture BaseColorMatTexture;
    BaseColorMatTexture.Texture = BaseColorTexture;
    BaseColorMatTexture.TextureChannel = EDMTextureChannelMask::RGB;

    // 4. 设置到纹理集
    MyTextureSet->SetMaterialTexture(EDMTextureSetMaterialProperty::BaseColor, BaseColorMatTexture);

    // 5. 查询并验证
    if (MyTextureSet->HasMaterialTexture(EDMTextureSetMaterialProperty::BaseColor))
    {
        FDMMaterialTexture OutTexture;
        MyTextureSet->GetMaterialTexture(EDMTextureSetMaterialProperty::BaseColor, OutTexture);
        UE_LOG(LogTemp, Warning, TEXT("Demo Success: BaseColor texture set to %s"), 
            OutTexture.Texture.IsValid() ? *OutTexture.Texture->GetName() : TEXT("Invalid"));
    }

    // 清理（临时纹理会随TransientPackage清理）
}
```

## 模块依赖

本插件的模块依赖关系较为复杂，且主要为内部模块间依赖。对于使用者而言，主要依赖 `DynamicMaterial` 和 `DynamicMaterialTextureSet` 运行时模块。

| 模块 | 用途 |
|---|---|
| `DynamicMaterial` | 核心运行时模块，提供材质创建和管理的基础框架。 |
| `DynamicMaterialTextureSet` | 提供纹理集（`UDMTextureSet`）及相关数据结构，是材质参数数据化的核心。 |
| `DynamicMaterialShaders` | 包含插件所需的自定义着色器代码。 |
| `DynamicMaterialEditor` | 编辑器模块，提供材质设计器的UI和编辑功能。 |
| `DynamicMaterialTextureSetEditor` | 纹理集资产的编辑器扩展和自定义界面。 |

## 维护状态

### 近期更新

- 2024-04-18 `d53ec51b85c0` Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction: ActorModifier, ActorModifierCore, Motion Design, ClonerEffector, CustomDetailsView, Material Designer, GeometryMask, OperatorStack, PropertyAnimator, PropertyAnimatorCore, StormSync, StormSync Motion Design Bridge
- 2024-04-18 `04930821cdf6` Run UnrealCodeFixup to add #include UE_INLINE_GENERATED_CPP_BY_NAME to files where possible
- 2024-04-18 `2a264ce3c015` Used UnrealCodeFixup to fix dll storage on code

### 维护评价

**创建时间**：2024年1月，是一个相对较新的插件。
**最近更新**：最近的提交（2024年4月）主要是将插件从 `Experimental` 目录移动到 `VirtualProduction` 目录，以及一些代码格式和编译修复，没有发现重大的功能更新或bug修复记录。
**维护状态**：**维护不活跃**。自创建并移入正式目录后，近一年内没有观察到实质性的功能开发或问题修复活动。
**推荐使用**：该插件功能明确，结构清晰，适合在虚拟制片项目中用于快速材质原型设计。但由于近期缺乏维护，使用者需自行评估其稳定性和与最新引擎版本的兼容性。建议在项目中使用前进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial)
- [官方文档]() (无)
- [测试用例]() (未在提供的路径中发现)