# Text 3D

> Tool to create 3D Text with advanced options

| 属性 | 值 |
|---|---|
| 分类 | Text |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、字体资源、蓝图资产） |
| 模块 | `Text3D` (Runtime), `Text3DEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Text3D) | |

## 用途

Text3D 是一个用于在 UE5 中创建和渲染 3D 文字的插件，专为虚拟制片（Virtual Production）场景设计。它不仅仅是简单的"把文字变成 3D 模型"，而是一套完整的 3D 文字排版与渲染系统。

**核心能力：**

- **字体解析与字形生成**：通过 FreeType2 和 HarfBuzz 库进行专业的字体解析、字形轮廓提取和文本整形（shaping），支持任意 TrueType/OpenType 字体
- **3D 几何生成**：将 2D 字形轮廓转换为 3D 网格，支持挤出（Extrude）、倒角（Bevel）、描边（Outline）等几何操作
- **富文本与样式系统**：支持类似 HTML 的标签语法（`<MyStyle>...</>`）和 Token 替换（`{MyToken}`），可在运行时动态改变文字内容和样式
- **可扩展架构**：采用 Extension 模式，将几何、布局、材质、渲染、样式、Token、字符、效果等逻辑分离为独立扩展，可被多个渲染器复用
- **布局控制**：完整的文本排版控制，包括字间距、行间距、对齐方式、最大宽高限制、自动缩放等
- **材质系统**：内置多种材质风格（纯色、渐变、纹理），支持前/后/挤出/倒角四个面的独立材质设置

**为什么存在：** UE5 原生不提供高质量的 3D 文字渲染能力。传统的做法是用 TextRenderComponent（仅支持平面文字）或手动建模。Text3D 插件填补了这一空白，特别适合虚拟制片中的标题、字幕、UI 元素等需要 3D 文字效果的场景。

## 使用场景

- **虚拟制片**：在 LED 墙场景中放置 3D 标题或字幕，需要实时调整文字内容和样式
- **动态 UI/HUD**：游戏或应用中需要 3D 效果的标题文字，可通过蓝图或 Sequencer 动画控制
- **品牌展示**：产品发布会、虚拟舞台等场景中需要高质量 3D 文字效果
- **数据驱动文字**：通过 Token 系统实现远程控制或数据绑定，动态替换文字中的变量部分
- **批量文字生产**：利用 StyleSet 和样式标签系统，统一管理大量文字的视觉风格

## 蓝图用法

### 核心组件

Text3D 的使用围绕 `UText3DComponent` 展开，可以直接添加到任何 Actor 上，也可以使用预置的 `AText3DActor`。

### 文本内容控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetText` | 设置文本内容，触发网格重建 | `UText3DComponent` |
| `GetText` | 获取当前文本 | `UText3DComponent` |
| `GetFormattedText` | 获取经过 Token 替换后的格式化文本 | `UText3DComponent` |
| `SetFont` | 设置字体 | `UText3DComponent` |
| `SetEnforceUpperCase` | 强制大写显示 | `UText3DComponent` |

### 几何参数控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetExtrude` | 设置挤出深度 | `UText3DDefaultGeometryExtension` |
| `SetBevel` | 设置倒角大小 | `UText3DDefaultGeometryExtension` |
| `SetBevelType` | 设置倒角类型（线性/半圆/凸/凹等） | `UText3DDefaultGeometryExtension` |
| `SetBevelSegments` | 设置倒角细分段数 | `UText3DDefaultGeometryExtension` |
| `SetUseOutline` | 启用/禁用描边 | `UText3DDefaultGeometryExtension` |
| `SetOutline` | 设置描边宽度 | `UText3DDefaultGeometryExtension` |
| `SetOutlineType` | 设置描边类型（Stroke/Fill） | `UText3DDefaultGeometryExtension` |
| `SetPivotHAlignment` | 设置枢轴水平对齐 | `UText3DDefaultGeometryExtension` |
| `SetPivotVAlignment` | 设置枢轴垂直对齐 | `UText3DDefaultGeometryExtension` |

### 布局控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetTracking` | 设置字间距 | `UText3DDefaultLayoutExtension` |
| `SetLineSpacing` | 设置行间距 | `UText3DDefaultLayoutExtension` |
| `SetWordSpacing` | 设置词间距 | `UText3DDefaultLayoutExtension` |
| `SetHorizontalAlignment` | 设置水平对齐方式 | `UText3DDefaultLayoutExtension` |
| `SetVerticalAlignment` | 设置垂直对齐方式 | `UText3DDefaultLayoutExtension` |
| `SetUseMaxWidth` | 启用最大宽度限制 | `UText3DDefaultLayoutExtension` |
| `SetMaxWidth` | 设置最大宽度 | `UText3DDefaultLayoutExtension` |
| `SetUseMaxHeight` | 启用最大高度限制 | `UText3DDefaultLayoutExtension` |
| `SetMaxHeight` | 设置最大高度 | `UText3DDefaultLayoutExtension` |
| `SetScaleProportionally` | 等比缩放 | `UText3DDefaultLayoutExtension` |

### 材质控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetStyle` | 设置材质风格（Solid/Gradient/Texture/Custom） | `UText3DDefaultMaterialExtension` |
| `SetFrontColor` | 设置前面颜色 | `UText3DDefaultMaterialExtension` |
| `SetBackColor` | 设置背面颜色 | `UText3DDefaultMaterialExtension` |
| `SetExtrudeColor` | 设置挤出面颜色 | `UText3DDefaultMaterialExtension` |
| `SetBevelColor` | 设置倒角面颜色 | `UText3DDefaultMaterialExtension` |
| `SetGradientColorA` | 设置渐变起始颜色 | `UText3DDefaultMaterialExtension` |
| `SetGradientColorB` | 设置渐变结束颜色 | `UText3DDefaultMaterialExtension` |
| `SetGradientSmoothness` | 设置渐变平滑度 | `UText3DDefaultMaterialExtension` |
| `SetGradientOffset` | 设置渐变偏移 | `UText3DDefaultMaterialExtension` |
| `SetGradientRotation` | 设置渐变旋转 | `UText3DDefaultMaterialExtension` |

### 渲染属性控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCastShadow` | 设置是否投射阴影 | `UText3DDefaultRenderingExtension` |
| `SetCastHiddenShadow` | 设置隐藏时是否投射阴影 | `UText3DDefaultRenderingExtension` |
| `SetAffectDynamicIndirectLighting` | 设置是否影响动态间接光照 | `UText3DDefaultRenderingExtension` |
| `SetAffectIndirectLightingWhileHidden` | 设置隐藏时是否影响间接光照 | `UText3DDefaultRenderingExtension` |
| `SetHoldout` | 设置 Holdout 模式 | `UText3DDefaultRenderingExtension` |

### 变换效果（Layout Effects）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetLocationEnabled` | 启用位置偏移效果 | `UText3DLayoutTransformEffect` |
| `SetLocationProgress` | 设置位置偏移进度（0-1） | `UText3DLayoutTransformEffect` |
| `SetLocationOrder` | 设置位置偏移顺序 | `UText3DLayoutTransformEffect` |
| `SetLocationBegin` | 设置位置偏移起始值 | `UText3DLayoutTransformEffect` |
| `SetLocationEnd` | 设置位置偏移结束值 | `UText3DLayoutTransformEffect` |
| `SetLocationEaseCurve` | 设置位置缓动曲线 | `UText3DLayoutTransformEffect` |
| `SetRotationEnabled` | 启用旋转效果 | `UText3DLayoutTransformEffect` |
| `SetRotationProgress` | 设置旋转进度 | `UText3DLayoutTransformEffect` |
| `SetScaleEnabled` | 启用缩放效果 | `UText3DLayoutTransformEffect` |
| `SetScaleProgress` | 设置缩放进度 | `UText3DLayoutTransformEffect` |

### 样式控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetStyleSet` | 设置样式集资产 | `UText3DDefaultStyleExtension` |
| `SetStyleName` | 设置样式名称 | `UText3DStyleBase` |
| `SetFont` | 设置样式字体 | `UText3DStyleBase` |
| `SetFontSize` | 设置样式字号 | `UText3DStyleBase` |
| `SetFrontColor` | 设置样式前景色 | `UText3DStyleBase` |

### 使用示例（蓝图描述）

**创建基本 3D 文字：**
1. 在场景中放置 `Text3DActor`，或在任意 Actor 上添加 `Text3DComponent`
2. 在 Details 面板中设置 Text 属性为所需文字
3. 调整 Font、Extrude、Bevel 等几何参数
4. 在 Material 分组中设置颜色和材质风格

**使用 Token 实现动态文字：**
1. 在 Text3DComponent 的 Token 扩展中添加 Token，命名为 `PlayerName`
2. 设置 Text 为 `"Hello {PlayerName}!"`
3. 在运行时通过蓝图修改 Token 的 Content 属性，`{PlayerName}` 会被自动替换

**使用样式标签实现富文本：**
1. 在 Text3DComponent 的 Style 扩展中添加样式，命名为 `Highlight`，设置红色字体
2. 设置 Text 为 `"Normal text <Highlight>red text</> back to normal"`
3. 标签内的文字会应用对应样式的字体、颜色等属性

**使用变换效果实现逐字动画：**
1. 在 Text3DComponent 的 Layout/LayoutEffects 中添加 `TransformEffect`
2. 启用 Location，设置 Begin 为 `(0, 0, -100)`，End 为 `(0, 0, 0)`
3. 在 Sequencer 或蓝图中动画化 LocationProgress 从 0 到 1
4. 文字会逐字从下方飞入

## C++ 用法

### 头文件引入

```cpp
#include "Text3DComponent.h"
#include "Text3DActor.h"
#include "Text3DTypes.h"
```

### 基本用法

```cpp
// 创建 Text3D Actor 并设置文字
// 来源: Text3DActor.h, Text3DComponent.h

AText3DActor* TextActor = GetWorld()->SpawnActor<AText3DActor>();
UText3DComponent* TextComp = TextActor->GetText3DComponent();

// 设置文本内容
TextComp->SetText(FText::FromString(TEXT("Hello 3D World!")));

// 设置字体
TextComp->SetFont(SomeFont);

// 设置挤出深度和倒角
TextComp->SetExtrude(20.0f);
TextComp->SetBevel(5.0f);
TextComp->SetBevelType(EText3DBevelType::Convex);
```

### 几何参数控制

```cpp
// 来源: Text3DDefaultGeometryExtension.h

// 获取几何扩展并配置
auto* GeomExt = TextComp->GetExtension<UText3DDefaultGeometryExtension>();

// 挤出与倒角
GeomExt->SetExtrude(30.0f);
GeomExt->SetBevel(8.0f);
GeomExt->SetBevelType(EText3DBevelType::HalfCircle);
GeomExt->SetBevelSegments(4);

// 描边
GeomExt->SetUseOutline(true);
GeomExt->SetOutline(3.0f);
GeomExt->SetOutlineType(EText3DOutlineType::Fill);

// 枢轴对齐
GeomExt->SetPivotHAlignment(EText3DHorizontalTextAlignment::Center);
GeomExt->SetPivotVAlignment(EText3DVerticalTextAlignment::Center);
```

### 布局控制

```cpp
// 来源: Text3DDefaultLayoutExtension.h

auto* LayoutExt = TextComp->GetExtension<UText3DDefaultLayoutExtension>();

// 间距控制
LayoutExt->SetTracking(1.2f);
LayoutExt->SetLineSpacing(1.5f);
LayoutExt->SetWordSpacing(1.0f);

// 对齐方式
LayoutExt->SetHorizontalAlignment(EText3DHorizontalTextAlignment::Center);
LayoutExt->SetVerticalAlignment(EText3DVerticalTextAlignment::Center);

// 最大尺寸限制
LayoutExt->SetUseMaxWidth(true);
LayoutExt->SetMaxWidth(500.0f);
LayoutExt->SetScaleProportionally(true);
```

### 材质控制

```cpp
// 来源: Text3DDefaultMaterialExtension.h

auto* MatExt = TextComp->GetExtension<UText3DDefaultMaterialExtension>();

// 纯色模式
MatExt->SetStyle(EText3DMaterialStyle::Solid);
MatExt->SetFrontColor(FLinearColor::Red);
MatExt->SetBackColor(FLinearColor::DarkRed);
MatExt->SetExtrudeColor(FLinearColor(0.8f, 0.0f, 0.0f));
MatExt->SetBevelColor(FLinearColor(1.0f, 0.2f, 0.2f));

// 渐变模式
MatExt->SetStyle(EText3DMaterialStyle::Gradient);
MatExt->SetGradientColorA(FLinearColor::Blue);
MatExt->SetGradientColorB(FLinearColor::Cyan);
MatExt->SetGradientSmoothness(0.5f);
MatExt->SetGradientRotation(45.0f);
```

### 渲染属性控制

```cpp
// 来源: Text3DDefaultRenderingExtension.h

auto* RenderExt = TextComp->GetExtension<UText3DDefaultRenderingExtension>();

RenderExt->SetCastShadow(true);
RenderExt->SetCastHiddenShadow(false);
RenderExt->SetAffectDynamicIndirectLighting(true);
RenderExt->SetAffectIndirectLightingWhileHidden(false);
RenderExt->SetHoldout(false);
```

### 变换效果（逐字动画）

```cpp
// 来源: Text3DLayoutTransformEffect.h

auto* TransformEffect = TextComp->GetExtension<UText3DLayoutTransformEffect>();

// 位置偏移效果
TransformEffect->SetLocationEnabled(true);
TransformEffect->SetLocationProgress(0.5f);  // 0-1 控制动画进度
TransformEffect->SetLocationOrder(EText3DCharacterEffectOrder::FromStart);
TransformEffect->SetLocationBegin(FVector(0, 0, -200));
TransformEffect->SetLocationEnd(FVector::ZeroVector);

// 旋转效果
TransformEffect->SetRotationEnabled(true);
TransformEffect->SetRotationProgress(0.75f);
TransformEffect->SetRotationBegin(FRotator(0, -90, 0));
TransformEffect->SetRotationEnd(FRotator::ZeroRotator);

// 缩放效果
TransformEffect->SetScaleEnabled(true);
TransformEffect->SetScaleProgress(1.0f);
TransformEffect->SetScaleBegin(FVector::ZeroVector);
TransformEffect->SetScaleEnd(FVector::OneVector);
```

### Token 替换（动态文字）

```cpp
// 来源: Text3DTokenBase.h, Text3DDefaultTokenExtension.h

// Token 系统通过蓝图配置更方便，C++ 中主要通过扩展接口访问
// 设置包含 Token 的文本
TextComp->SetText(FText::FromString(TEXT("Score: {PlayerScore}")));

// Token 的内容替换通过 UText3DTokenBase 的 SetContent 方法
// 在蓝图中配置 Token 数组更直观
```

### 样式系统

```cpp
// 来源: Text3DStyleBase.h, Text3DDefaultStyleExtension.h

auto* StyleExt = TextComp->GetExtension<UText3DDefaultStyleExtension>();

// 设置样式集资产
StyleExt->SetStyleSet(SomeStyleSetAsset);

// 样式标签用法：在文本中使用 <StyleName>...</> 标记
TextComp->SetText(FText::FromString(TEXT("Normal <Bold>bold text</> normal")));
```

### 监听文本更新

```cpp
// 来源: Text3DComponent.h

// 原生委托
TextComp->OnTextGenerated().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("Text3D has been regenerated"));
});

// 带标志的更新委托
TextComp->OnTextPostUpdate().AddLambda([](UText3DComponent* Comp, EText3DRendererFlags Flags)
{
    if (EnumHasAnyFlags(Flags, EText3DRendererFlags::Geometry))
    {
        UE_LOG(LogTemp, Log, TEXT("Geometry was updated"));
    }
});

// 蓝图委托
TextComp->OnTextGenerated.AddDynamic(this, &AMyActor::OnTextRegenerated);
```

### 进阶用法：自定义扩展

```cpp
// 来源: Text3DExtensionBase.h 及各扩展基类

// Text3D 的扩展系统允许创建自定义扩展
// 继承对应的基类并实现虚函数即可

// 自定义几何扩展
UCLASS()
class UMyGeometryExtension : public UText3DGeometryExtensionBase
{
    GENERATED_BODY()
public:
    UMyGeometryExtension()
        : UText3DGeometryExtensionBase()
    {}

    virtual EText3DHorizontalTextAlignment GetGlyphHAlignment() const override
    {
        return EText3DHorizontalTextAlignment::Center;
    }

    virtual EText3DVerticalTextAlignment GetGlyphVAlignment() const override
    {
        return EText3DVerticalTextAlignment::Center;
    }
};

// 自定义效果扩展
UCLASS()
class UMyCustomEffect : public UText3DEffectExtensionBase
{
    GENERATED_BODY()
public:
    virtual FText3DRange GetTargetRange() const override
    {
        // 对所有字符生效
        return FText3DRange();
    }

    virtual void ApplyEffect(uint32 InCharacterIndex, uint32 InCharacterCount) override
    {
        // 自定义效果逻辑
    }
};
```

### 进阶用法：字符级控制

```cpp
// 来源: Text3DCharacterBase.h, Text3DDefaultCharacter.h

auto* CharExt = TextComp->GetExtension<UText3DDefaultCharacterExtension>();

// 获取字符数量
uint16 CharCount = CharExt->GetCharacterCount();

// 遍历并控制每个字符
for (uint16 i = 0; i < CharCount; ++i)
{
    UText3DCharacterBase* Char = CharExt->GetCharacter(i);
    if (Char)
    {
        // 设置单个字符的位置、旋转、缩放
        Char->SetRelativeLocation(FVector(i * 50.0f, 0, 0));
        Char->SetRelativeRotation(FRotator(0, 15.0f * i, 0));
        Char->SetRelativeScale(FVector(1.0f + i * 0.1f));
        
        // 设置可见性
        Char->SetVisibility(true);
        
        // 自定义字间距（UText3DDefaultCharacter 特有）
        auto* DefaultChar = Cast<UText3DDefaultCharacter>(Char);
        if (DefaultChar)
        {
            DefaultChar->SetKerning(5.0f);
        }
    }
}
```

## Demo 示例

### 基本 3D 文字组件

```cpp
// MyText3DActor.h
#pragma once

#include "GameFramework/Actor.h"
#include "MyText3DActor.generated.h"

class UText3DComponent;
class UText3DDefaultGeometryExtension;
class UText3DDefaultLayoutExtension;
class UText3DDefaultMaterialExtension;
class UText3DDefaultRenderingExtension;
class UText3DLayoutTransformEffect;

UCLASS()
class AMyText3DActor : public AActor
{
    GENERATED_BODY()

public:
    AMyText3DActor();

    /** 动画化变换效果进度 */
    UFUNCTION(BlueprintCallable)
    void AnimateTransformProgress(float InProgress);

    /** 切换材质风格 */
    UFUNCTION(BlueprintCallable)
    void SwitchToGradientStyle();

    /** 更新文本内容 */
    UFUNCTION(BlueprintCallable)
    void UpdateText(const FString& NewText);

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UText3DComponent> Text3DComponent;

private:
    /** 文本生成完成回调 */
    UFUNCTION()
    void OnTextGenerated();
};
```

```cpp
// MyText3DActor.cpp
#include "MyText3DActor.h"
#include "Text3DComponent.h"
#include "Extensions/Text3DDefaultGeometryExtension.h"
#include "Extensions/Text3DDefaultLayoutExtension.h"
#include "Extensions/Text3DDefaultMaterialExtension.h"
#include "Extensions/Text3DDefaultRenderingExtension.h"
#include "Extensions/Text3DLayoutTransformEffect.h"

AMyText3DActor::AMyText3DActor()
{
    Text3DComponent = CreateDefaultSubobject<UText3DComponent>(TEXT("Text3D"));
    RootComponent = Text3DComponent;
}

void AMyText3DActor::BeginPlay()
{
    Super::BeginPlay();

    // 设置文本内容
    Text3DComponent->SetText(FText::FromString(TEXT("Hello 3D World!")));

    // 配置几何参数
    Text3DComponent->SetExtrude(25.0f);
    Text3DComponent->SetBevel(5.0f);
    Text3DComponent->SetBevelType(EText3DBevelType::Convex);
    Text3DComponent->SetBevelSegments(3);

    // 配置布局
    Text3DComponent->SetTracking(1.1f);
    Text3DComponent->SetLineSpacing(1.2f);
    Text3DComponent->SetHorizontalAlignment(EText3DHorizontalTextAlignment::Center);
    Text3DComponent->SetVerticalAlignment(EText3DVerticalTextAlignment::Center);

    // 配置材质 - 纯色模式
    Text3DComponent->SetStyle(EText3DMaterialStyle::Solid);
    Text3DComponent->SetFrontColor(FLinearColor(0.2f, 0.6f, 1.0f));
    Text3DComponent->SetBackColor(FLinearColor(0.1f, 0.3f, 0.5f));
    Text3DComponent->SetExtrudeColor(FLinearColor(0.15f, 0.45f, 0.75f));
    Text3DComponent->SetBevelColor(FLinearColor(0.3f, 0.7f, 1.0f));

    // 配置渲染属性
    Text3DComponent->SetCastShadow(true);

    // 监听文本生成完成
    Text3DComponent->OnTextGenerated.AddDynamic(this, &AMyText3DActor::OnTextGenerated);
}

void AMyText3DActor::AnimateTransformProgress(float InProgress)
{
    // 需要在蓝图中预先添加 TransformEffect 扩展
    // 这里演示如何通过 C++ 控制进度
    // 实际使用中，TransformEffect 通常在编辑器中配置
}

void AMyText3DActor::SwitchToGradientStyle()
{
    Text3DComponent->SetStyle(EText3DMaterialStyle::Gradient);
    Text3DComponent->SetGradientColorA(FLinearColor::Blue);
    Text3DComponent->SetGradientColorB(FLinearColor::Cyan);
    Text3DComponent->SetGradientSmoothness(0.5f);
    Text3DComponent->SetGradientRotation(45.0f);
}

void AMyText3DActor::UpdateText(const FString& NewText)
{
    Text3DComponent->SetText(FText::FromString(NewText));
}

void AMyText3DActor::OnTextGenerated()
{
    UE_LOG(LogTemp, Log, TEXT("Text3D regenerated: bounds = %s"),
        *Text3DComponent->GetBounds().ToString());
}
```

## 模块依赖

### Text3D (Runtime)

| 模块 | 用途 |
|---|---|
| `FreeType2` | 字体文件解析，提取字形轮廓数据 |
| `HarfBuzz` | 文本整形引擎，处理复杂文本排版（连字、双向文本等） |
| `MeshMergeUtilities` | 网格合并工具，用于将多个字符网格合并为单一网格 |

### Text3DEditor (Editor)

| 模块 | 用途 |
|---|---|
| `DirectX` | 编辑器中字体渲染相关的 DirectX 支持 |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `GeometryProcessing` | 几何处理算法，用于字形网格的生成和优化 |
| `GeometryScripting` | 几何脚本接口，用于程序化网格操作 |
| `GeometryMask` | 几何遮罩，用于材质和渲染相关的几何操作 |

## 维护状态

### 近期更新

```
- e9e82938a92 MotionDesign : Text3D - Fixed compilation error caused by Freetype usage outside macros for an UnrealServer build
- c74f3b7267a MotionDesign : Text3D - Fixed crash caused by an invalid character object/mesh, the causes are unknown due to missing repro steps, but this will add additional checks for safety
- 4dfd2b49a86 MotionDesign : - Various minimal fixes for ActorModifier, PropertyAnimator and Text3D
```

- `e9e82938a92`：修复了 FreeType 在 UnrealServer 构建中的编译错误，说明该插件在服务器端构建场景中也有使用
- `c74f3b7267a`：修复了无效字符对象/网格导致的崩溃，增加了安全检查。commit 中提到"原因未知，缺少复现步骤"，表明这是一个防御性修复
- `4dfd2b49a86`：与其他 MotionDesign 插件（ActorModifier、PropertyAnimator）一起的小型修复

### 维护评价

**活跃维护中**。Text3D 插件属于 Epic 的 MotionDesign（动态设计）工具链的一部分，与 ActorModifier、PropertyAnimator 等插件协同维护。从最近的 commit 来看：

- **持续更新**：最近的提交集中在 bug 修复和稳定性提升，说明该插件仍在积极使用和维护
- **架构成熟**：源码中可以看到完整的版本迁移系统（`FText3DComponentVersion`），从旧版 `UText3DCharacterTransform` 迁移到新的 Extension 系统，说明经历了重大重构
- **依赖专业库**：使用 FreeType2 和 HarfBuzz 这两个业界标准的字体处理库，保证了字体渲染的质量和兼容性
- **扩展性设计**：Extension 架构允许自定义渲染器和效果，为未来扩展留有空间
- **已知限制**：commit 中提到的崩溃问题"缺少复现步骤"，暗示在某些边缘情况下可能存在稳定性问题

**推荐使用**。对于需要 3D 文字的虚拟制片项目，这是 Epic 官方提供的最完善的解决方案。插件架构成熟，API 丰富，支持蓝图和 C++ 两种使用方式。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Text3D)
- [官方文档]()（暂无）