# Material Designer

> Compact dynamic material creator and editor, similar in style to other DDCs.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、纹理集资产、着色器） |
| 模块 | `DynamicMaterial` (RuntimeAndProgram), `DynamicMaterialTextureSet` (RuntimeAndProgram), `DynamicMaterialEditor` (Editor), `DynamicMaterialTextureSetEditor` (Editor), `DynamicMaterialShaders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial) | |

## 用途

Material Designer 是一个**基于组件的动态材质创建与编辑系统**，让你无需打开传统材质编辑器（Material Editor），就能通过一个精简的属性面板式界面构建材质。

它解决的核心问题是：**传统材质编辑器过于复杂，对于虚拟制片中常见的快速材质调整场景（如实时修改颜色、纹理、粗糙度等参数），需要一个更轻量、更数据驱动的方案。**

具体来说：
- **数据驱动材质**：通过 `UDynamicMaterialModel` 定义材质结构，运行时通过 `UDynamicMaterialInstance`（继承自 `UMaterialInstanceDynamic`）实例化并应用
- **组件化架构**：每个材质属性（BaseColor、Roughness、Normal 等）由独立的组件（Stage/Slot）控制，每个组件包含可参数化的值（Float、Color、Texture 等）
- **动态实例系统**：提供完整的 Dynamic 变体（`UDMMaterialValueDynamic`），支持在运行时覆盖材质参数而不修改原始模型
- **渲染目标集成**：支持将 UMG Widget 渲染到 RenderTarget 并作为纹理输入材质
- **纹理集（TextureSet）**：提供纹理集管理功能，将多个纹理打包为一组材质属性

## 使用场景

- 你在做虚拟制片项目，需要在运行时快速调整材质参数（颜色、粗糙度、金属度等） → 用 Material Designer 的动态值系统
- 你需要一个精简的材质编辑界面，不想打开完整的材质编辑器 → 用 Material Designer 的组件化编辑器
- 你需要将 UMG Widget 实时渲染为纹理并应用到材质上 → 用 `UDMRenderTargetUMGWidgetRenderer`
- 你需要管理一组纹理（如 PBR 贴图集：BaseColor + Normal + ORM）→ 用 DynamicMaterialTextureSet 模块
- 你需要在蓝图中动态创建和修改材质，而不想手动管理材质表达式节点 → 用 Material Designer 的 Model/Value 系统

## 模块架构

```
DynamicMaterial/
├── DynamicMaterial/              ← 核心运行时（组件、值、模型、材质实例）
├── DynamicMaterialTextureSet/    ← 纹理集运行时
├── DynamicMaterialEditor/        ← 编辑器 UI（属性面板、自定义细节视图）
├── DynamicMaterialTextureSetEditor/ ← 纹理集编辑器
└── DynamicMaterialShaders/       ← 自定义着色器（PostConfigInit 加载）
```

### 核心概念

| 概念 | 类 | 说明 |
|---|---|---|
| 材质实例 | `UDynamicMaterialInstance` | 继承自 `UMaterialInstanceDynamic`，包含自己的 Model |
| 材质模型 | `UDynamicMaterialModel` | 定义材质结构（哪些属性用哪些组件） |
| 模型基类 | `UDynamicMaterialModelBase` | Model 和 ModelInstance 的共同基类 |
| 材质值 | `UDMMaterialValue` 及子类 | 可参数化的值（Float、Color、Texture 等） |
| 动态值 | `UDMMaterialValueDynamic` 及子类 | 运行时可覆盖的值实例 |
| 材质参数 | `UDMMaterialParameter` | 注册到 Model 的命名参数 |
| 渲染目标渲染器 | `UDMRenderTargetRenderer` | 将内容渲染到 RenderTarget |
| 纹理 UV | `UDMTextureUV` / `UDMTextureUVDynamic` | 纹理坐标控制（偏移、旋转、平铺） |

### 值类型体系

```
UDMMaterialValue (抽象基类)
├── UDMMaterialValueBool          ← bool
├── UDMMaterialValueFloat (抽象)  ← 浮点基类
│   ├── UDMMaterialValueFloat1    ← float
│   ├── UDMMaterialValueFloat2    ← FVector2D
│   ├── UDMMaterialValueFloat3XYZ ← FVector
│   ├── UDMMaterialValueFloat3RGB ← FLinearColor (无 Alpha)
│   ├── UDMMaterialValueFloat3RPY ← FRotator
│   └── UDMMaterialValueFloat4    ← FLinearColor (含 Alpha)
├── UDMMaterialValueTexture       ← UTexture*
├── UDMMaterialValueColorAtlas    ← 颜色图集 (UCurveLinearColorAtlas)
└── UDMMaterialValueRenderTarget  ← 渲染目标纹理
```

每种值类型都有对应的 Dynamic 变体（如 `UDMMaterialValueFloat1Dynamic`），用于实例化材质的运行时参数覆盖。

## 蓝图用法

### 核心节点 — 材质实例

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMaterialModel` | 获取关联的材质模型 | `UDynamicMaterialInstance` |
| `GetMaterialModelBase` | 获取材质模型基类 | `UDynamicMaterialInstance` |
| `GetGeneratedMaterial` | 获取生成的 UMaterial | `UDynamicMaterialModelBase` |
| `ResolveMaterialModel` | 解析并返回基础材质模型 | `UDynamicMaterialModelBase` |
| `GetDynamicMaterialInstance` | 获取包含此模型的材质实例 | `UDynamicMaterialModelBase` |

### 核心节点 — 材质值（以 Float1 为例）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetValue` | 获取当前值 | `UDMMaterialValueFloat1` |
| `SetValue` | 设置值（会触发材质更新） | `UDMMaterialValueFloat1` |
| `GetDefaultValue` | 获取默认值（仅编辑器） | `UDMMaterialValueFloat1` |
| `SetDefaultValue` | 设置默认值（仅编辑器） | `UDMMaterialValueFloat1` |
| `GetValueRange` | 获取值范围 | `UDMMaterialValueFloat` |
| `HasValueRange` | 是否设置了值范围 | `UDMMaterialValueFloat` |
| `SetValueRange` | 设置值范围 | `UDMMaterialValueFloat` |

### 核心节点 — 动态值（运行时覆盖）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetValue` | 获取动态覆盖值 | `UDMMaterialValueFloat1Dynamic` |
| `SetValue` | 设置动态覆盖值 | `UDMMaterialValueFloat1Dynamic` |
| `GetParentValue` | 获取父模型中的原始值 | `UDMMaterialValueDynamic` |
| `IsDefaultValue` | 当前值是否与默认值相同 | `UDMMaterialValueDynamic` |
| `ApplyDefaultValue` | 恢复为默认值 | `UDMMaterialValueDynamic` |
| `SetMIDParameter` | 将值应用到 MID | `UDMMaterialValueDynamic` |

### 核心节点 — 渲染目标

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateRenderTargetRenderer` | 创建渲染目标渲染器 | `UDMRenderTargetRenderer` |
| `UpdateRenderTarget` | 更新渲染目标内容 | `UDMRenderTargetRenderer` |
| `AsyncUpdateRenderTarget` | 异步更新（帧末执行） | `UDMRenderTargetRenderer` |
| `GetRenderTarget` | 获取 UTextureRenderTarget2D | `UDMMaterialValueRenderTarget` |
| `SetTextureSize` | 设置渲染目标尺寸 | `UDMMaterialValueRenderTarget` |
| `SetTextureFormat` | 设置渲染目标格式 | `UDMMaterialValueRenderTarget` |
| `SetClearColor` | 设置清除颜色 | `UDMMaterialValueRenderTarget` |
| `SetWidgetClass` | 设置要渲染的 UMG Widget 类 | `UDMRenderTargetUMGWidgetRenderer` |

### 核心节点 — 纹理 UV

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetOffset` / `SetOffset` | 纹理偏移 | `UDMTextureUVDynamic` |
| `GetPivot` / `SetPivot` | 旋转/平铺的枢轴点 | `UDMTextureUVDynamic` |
| `GetRotation` / `SetRotation` | 纹理旋转 | `UDMTextureUVDynamic` |
| `GetTiling` / `SetTiling` | 纹理平铺 | `UDMTextureUVDynamic` |

### 核心节点 — 材质参数

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMaterialModel` | 获取所属的材质模型 | `UDMMaterialParameter` |
| `GetParameterName` | 获取参数名称 | `UDMMaterialParameter` |
| `RenameParameter` | 重命名参数（仅编辑器） | `UDMMaterialParameter` |

### 核心节点 — 值定义工具

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetValueTypes` | 获取所有可用值类型 | `UDMValueDefinitionLibrary` |
| `GetValueDefinition` | 获取指定值类型的定义 | `UDMValueDefinitionLibrary` |

### 使用示例（蓝图描述）

**场景：运行时修改材质参数**

1. 获取场景中使用 Material Designer 的 Actor 的材质实例（`UDynamicMaterialInstance`）
2. 调用 `GetMaterialModel` 获取材质模型
3. 通过模型获取特定的 `UDMMaterialValueFloat1`（如粗糙度值）
4. 调用 `SetValue(0.5)` 修改粗糙度
5. 材质会自动更新

**场景：运行时覆盖动态值**

1. 获取 `UDynamicMaterialModelDynamic`（动态模型实例）
2. 通过动态模型获取 `UDMMaterialValueFloat1Dynamic`
3. 调用 `SetValue` 设置运行时覆盖值
4. 调用 `SetMIDParameter` 将值应用到 `UMaterialInstanceDynamic`

**场景：将 UMG Widget 渲染为材质纹理**

1. 创建 `UDMMaterialValueRenderTarget` 并设置尺寸/格式
2. 调用 `CreateRenderTargetRenderer` 创建 `UDMRenderTargetUMGWidgetRenderer`
3. 调用 `SetWidgetClass` 指定要渲染的 Widget 类
4. 调用 `UpdateRenderTarget` 触发渲染
5. 渲染结果自动作为纹理输入到材质中

## C++ 用法

### 头文件引入

```cpp
// 核心模块
#include "DynamicMaterialModule.h"

// 材质实例和模型
#include "Material/DynamicMaterialInstance.h"
#include "Model/DynamicMaterialModelBase.h"

// 材质值
#include "Components/MaterialValues/DMMaterialValueFloat1.h"
#include "Components/MaterialValues/DMMaterialValueFloat4.h"
#include "Components/MaterialValues/DMMaterialValueTexture.h"
#include "Components/MaterialValues/DMMaterialValueRenderTarget.h"

// 动态值
#include "Components/MaterialValuesDynamic/DMMaterialValueFloat1Dynamic.h"
#include "Components/MaterialValuesDynamic/DMMaterialValueFloat4Dynamic.h"

// 渲染目标
#include "Components/DMRenderTargetRenderer.h"
#include "Components/RenderTargetRenderers/DMRenderTargetUMGWidgetRenderer.h"

// 纹理 UV
#include "Components/DMTextureUVDynamic.h"

// 定义和工具
#include "DMDefs.h"
#include "DMValueDefinition.h"
#include "Utils/DMUtils.h"
```

### 基本用法 — 检查模块状态

```cpp
// 来源: DynamicMaterialModule.h
#include "DynamicMaterialModule.h"

// 获取模块实例
FDynamicMaterialModule& Module = FDynamicMaterialModule::Get();

// 检查 UObject 是否安全使用（避免在 GC 期间操作）
if (FDynamicMaterialModule::AreUObjectsSafe())
{
    // 安全地操作材质对象
}

// 检查材质导出是否启用（通过控制台变量 DM.ExportMaterials）
if (FDynamicMaterialModule::IsMaterialExportEnabled())
{
    // 执行材质导出逻辑
}
```

### 基本用法 — 操作材质值

```cpp
// 来源: Components/MaterialValues/DMMaterialValueFloat1.h
#include "Components/MaterialValues/DMMaterialValueFloat1.h"

// 假设已获取 UDMMaterialValueFloat1* FloatValue
// 设置值
FloatValue->SetValue(0.75f);

// 获取值
float CurrentValue = FloatValue->GetValue();

// 设置值范围（可选）
FFloatInterval Range(0.0f, 1.0f);
FloatValue->SetValueRange(Range);

// 检查是否有值范围
if (FloatValue->HasValueRange())
{
    const FFloatInterval& ValueRange = FloatValue->GetValueRange();
}
```

### 基本用法 — 操作颜色值

```cpp
// 来源: Components/MaterialValues/DMMaterialValueFloat4.h
#include "Components/MaterialValues/DMMaterialValueFloat4.h"

// UDMMaterialValueFloat4* ColorValue
// 设置颜色（含 Alpha）
ColorValue->SetValue(FLinearColor(1.0f, 0.5f, 0.0f, 1.0f));

// 获取颜色
const FLinearColor& Color = ColorValue->GetValue();
```

### 基本用法 — 操作纹理值

```cpp
// 来源: Components/MaterialValues/DMMaterialValueTexture.h
#include "Components/MaterialValues/DMMaterialValueTexture.h"

// UDMMaterialValueTexture* TextureValue
// 设置纹理
UTexture* MyTexture = LoadObject<UTexture>(nullptr, TEXT("/Game/Textures/T_MyTexture"));
TextureValue->SetValue(MyTexture);

// 获取纹理
UTexture* CurrentTexture = TextureValue->GetValue();

// 检查纹理是否有 Alpha 通道
if (TextureValue->HasAlpha())
{
    // 处理有 Alpha 的纹理
}
```

### 进阶用法 — 动态值系统（运行时参数覆盖）

```cpp
// 来源: Components/MaterialValuesDynamic/DMMaterialValueFloat1Dynamic.h
// 来源: Components/DMMaterialValueDynamic.h
#include "Components/MaterialValuesDynamic/DMMaterialValueFloat1Dynamic.h"
#include "Components/DMMaterialValueDynamic.h"

// 创建动态值（通常由 DynamicMaterialModelDynamic 自动管理）
// UDMMaterialValueFloat1Dynamic* DynamicFloat = 
//     UDMMaterialValueDynamic::CreateValueDynamic<UDMMaterialValueFloat1Dynamic>(
//         MaterialModelDynamic, ParentValue);

// 设置运行时覆盖值
DynamicFloat->SetValue(0.3f);

// 获取父模型中的原始值
UDMMaterialValue* ParentValue = DynamicFloat->GetParentValue();

// 检查是否与默认值相同
if (DynamicFloat->IsDefaultValue())
{
    // 值未被修改
}

// 恢复为默认值
DynamicFloat->ApplyDefaultValue();

// 将值应用到 MID
UMaterialInstanceDynamic* MID = /* 获取 MID */;
DynamicFloat->SetMIDParameter(MID);
```

### 进阶用法 — 渲染目标系统

```cpp
// 来源: Components/DMRenderTargetRenderer.h
// 来源: Components/MaterialValues/DMMaterialValueRenderTarget.h
#include "Components/DMRenderTargetRenderer.h"
#include "Components/MaterialValues/DMMaterialValueRenderTarget.h"
#include "Components/RenderTargetRenderers/DMRenderTargetUMGWidgetRenderer.h"

// 创建渲染目标渲染器
// UDMMaterialValueRenderTarget* RTValue = /* 获取渲染目标值 */;
UDMRenderTargetRenderer* Renderer = UDMRenderTargetRenderer::CreateRenderTargetRenderer(
    UDMRenderTargetUMGWidgetRenderer::StaticClass(), RTValue);

// 或使用模板版本
UDMRenderTargetUMGWidgetRenderer* WidgetRenderer = 
    UDMRenderTargetRenderer::CreateRenderTargetRenderer<UDMRenderTargetUMGWidgetRenderer>(RTValue);

// 设置 Widget 类
WidgetRenderer->SetWidgetClass(UMyWidget::StaticClass());

// 同步更新渲染目标
WidgetRenderer->UpdateRenderTarget();

// 或异步更新（帧末执行）
WidgetRenderer->AsyncUpdateRenderTarget();

// 刷新待处理的更新
WidgetRenderer->FlushUpdateRenderTarget();

// 检查是否正在更新
if (Renderer->IsUpdating())
{
    // 渲染目标正在重新渲染
}
```

### 进阶用法 — 渲染目标配置

```cpp
// 来源: Components/MaterialValues/DMMaterialValueRenderTarget.h
#include "Components/MaterialValues/DMMaterialValueRenderTarget.h"

// UDMMaterialValueRenderTarget* RTValue
// 设置渲染目标尺寸
RTValue->SetTextureSize(FIntPoint(512, 512));

// 设置渲染目标格式
RTValue->SetTextureFormat(RTF_RGBA8);

// 设置清除颜色
RTValue->SetClearColor(FLinearColor::Black);

// 获取渲染目标纹理
UTextureRenderTarget2D* RT = RTValue->GetRenderTarget();

// 确保渲染目标有效
RTValue->EnsureRenderTarget();       // 同步创建
RTValue->EnsureRenderTarget(true);   // 异步创建（帧末）
```

### 进阶用法 — 纹理 UV 动态控制

```cpp
// 来源: Components/DMTextureUVDynamic.h
#include "Components/DMTextureUVDynamic.h"

// UDMTextureUVDynamic* TextureUV = /* 获取动态纹理 UV */;

// 设置偏移
TextureUV->SetOffset(FVector2D(0.1f, 0.2f));

// 设置枢轴点（旋转和平铺的中心）
TextureUV->SetPivot(FVector2D(0.5f, 0.5f));

// 设置旋转（度数）
TextureUV->SetRotation(45.0f);

// 设置平铺
TextureUV->SetTiling(FVector2D(2.0f, 2.0f));

// 将 UV 参数应用到 MID
UMaterialInstanceDynamic* MID = /* 获取 MID */;
TextureUV->SetMIDParameters(MID);
```

### 进阶用法 — 材质属性类型转换

```cpp
// 来源: Utils/DMUtils.h
#include "Utils/DMUtils.h"
#include "DMDefs.h"

// Material Designer 属性类型与引擎材质属性之间的转换
EDMMaterialPropertyType DMType = EDMMaterialPropertyType::BaseColor;

// 转换为引擎材质属性
EMaterialProperty EngineProperty = FDMUtils::MaterialPropertyTypeToMaterialProperty(DMType);

// 从引擎材质属性转换回来
EDMMaterialPropertyType DMTypeBack = FDMUtils::MaterialPropertyToMaterialPropertyType(EngineProperty);

// 转换为纹理集材质属性
EDMTextureSetMaterialProperty TextureSetProp = 
    FDMUtils::MaterialPropertyTypeToTextureSetMaterialProperty(DMType);
```

### 进阶用法 — 组件路径解析

```cpp
// 来源: DMComponentPath.h
#include "DMComponentPath.h"

// 组件路径格式: "Name.Component.Component[2].Value"
FDMComponentPath Path(TEXT("MyModel.Slot[0].Stage.Value"));

// 获取第一个路径段
FDMComponentPathSegment Segment = Path.GetFirstSegment();
FStringView Token = Segment.GetToken();  // "MyModel"

// 检查是否有参数
if (Segment.HasParameter())
{
    int32 IntParam;
    if (Segment.GetParameter(IntParam))
    {
        // 使用整数参数
    }
    
    FString StringParam;
    if (Segment.GetParameter(StringParam))
    {
        // 使用字符串参数
    }
}

// 检查是否是叶子节点
if (Path.IsLeaf())
{
    // 路径已解析完毕
}
```

### 进阶用法 — 参数容器接口

```cpp
// 来源: IDMParameterContainer.h
#include "IDMParameterContainer.h"

// IDMParameterContainer 是一个接口，用于在对象之间复制参数值
// 实现此接口的类包括所有 DMMaterialValue*Dynamic 和 UDMRenderTargetUMGWidgetRenderer

// 在两个同类型对象之间复制参数
UObject* Source = /* 源对象 */;
UObject* Dest = /* 目标对象 */;
IDMParameterContainer::CopyParametersBetween(Source, Dest);

// 或通过接口方法
// IDMParameterContainer* Container = /* 获取接口 */;
// Container->CopyParametersTo(OtherObject);
// Container->CopyParametersFromWrapper(OtherObject);
```

## Demo 示例

### 最小示例 — 创建动态材质并修改参数

```cpp
// MyMaterialModifier.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyMaterialModifier.generated.h"

class UDynamicMaterialInstance;
class UDMMaterialValueFloat1;
class UDMMaterialValueFloat4;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyMaterialModifier : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyMaterialModifier();

    UFUNCTION(BlueprintCallable)
    void SetRoughness(float InRoughness);

    UFUNCTION(BlueprintCallable)
    void SetBaseColor(const FLinearColor& InColor);

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    TObjectPtr<UDynamicMaterialInstance> DynamicMaterial;

    UPROPERTY()
    TObjectPtr<UDMMaterialValueFloat1> RoughnessValue;

    UPROPERTY()
    TObjectPtr<UDMMaterialValueFloat4> BaseColorValue;
};
```

```cpp
// MyMaterialModifier.cpp
#include "MyMaterialModifier.h"
#include "Material/DynamicMaterialInstance.h"
#include "Model/DynamicMaterialModelBase.h"
#include "Components/MaterialValues/DMMaterialValueFloat1.h"
#include "Components/MaterialValues/DMMaterialValueFloat4.h"
#include "DynamicMaterialModule.h"

UMyMaterialModifier::UMyMaterialModifier()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyMaterialModifier::BeginPlay()
{
    Super::BeginPlay();

    if (!FDynamicMaterialModule::AreUObjectsSafe())
    {
        return;
    }

    // 获取 Actor 上的 Material Designer 材质实例
    // （假设已在编辑器中设置好材质）
    AActor* Owner = GetOwner();
    if (!Owner)
    {
        return;
    }

    UPrimitiveComponent* PrimComp = Owner->FindComponentByClass<UPrimitiveComponent>();
    if (!PrimComp)
    {
        return;
    }

    // 获取材质并检查是否为 DynamicMaterialInstance
    UMaterialInterface* MatInterface = PrimComp->GetMaterial(0);
    DynamicMaterial = Cast<UDynamicMaterialInstance>(MatInterface);

    if (!DynamicMaterial)
    {
        return;
    }

    // 获取材质模型并查找值组件
    // 注意：实际使用中需要通过组件路径或编辑器设置来获取具体值
    // 这里演示概念性用法
}

void UMyMaterialModifier::SetRoughness(float InRoughness)
{
    if (RoughnessValue)
    {
        RoughnessValue->SetValue(FMath::Clamp(InRoughness, 0.0f, 1.0f));
    }
}

void UMyMaterialModifier::SetBaseColor(const FLinearColor& InColor)
{
    if (BaseColorValue)
    {
        BaseColorValue->SetValue(InColor);
    }
}
```

## 模块依赖

从模块类型和插件依赖推断，使用者需要注意以下依赖：

| 模块 | 用途 |
|---|---|
| `CustomDetailsView` | 插件级依赖，提供自定义细节面板视图（编辑器 UI 用） |
| `DynamicMaterial` | 核心运行时模块，所有材质值/组件/模型的基础 |
| `DynamicMaterialEditor` | 编辑器模块，提供 Material Designer 的编辑器 UI |
| `DynamicMaterialTextureSet` | 纹理集运行时模块 |
| `DynamicMaterialTextureSetEditor` | 纹理集编辑器模块 |
| `DynamicMaterialShaders` | 自定义着色器模块（PostConfigInit 阶段加载） |

**使用建议**：
- 如果只需要运行时操作材质参数 → 依赖 `DynamicMaterial`
- 如果需要纹理集功能 → 额外依赖 `DynamicMaterialTextureSet`
- 如果需要编辑器集成 → 额外依赖 `DynamicMaterialEditor`
- 无特殊依赖（仅标准 Core/Engine/Slate 等），但需要 `CustomDetailsView` 插件启用

## 维护状态

### 近期更新

```
- f70998fa Material Designer: Refactored the 'channel bitmask' function to reduce node count and give better output.
- a02418ff Material Designer: Fixed packaging issue related to class export.
- 04930821 Run UnrealCodeFixup to add #include UE_INLINE_GENERATED_CPP_BY_NAME to files where possible
```

### 维护评价

- **创建时间**：2024 年 1 月，是一个相对较新的插件
- **代码规模**：1148 个源文件，属于大型插件，架构完整
- **维护状态**：活跃维护中。近期提交包含功能优化（减少材质节点数量）和打包问题修复，表明仍在积极开发
- **来源**：由 Epic Games 官方开发和维护，属于 Virtual Production 分类
- **实验性**：`.uplugin` 中 `Installed: false`，说明需要手动启用
- **架构成熟度**：组件化设计完善，支持 JSON 序列化、动态实例、渲染目标等高级功能

**推荐使用**：✅ 推荐。这是一个由 Epic 官方维护的虚拟制片工具，架构成熟，功能完整。适合需要在运行时灵活控制材质参数的虚拟制片和交互式应用项目。由于 `Installed: false`，需要在项目设置中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial)
- [核心运行时模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial/Source/DynamicMaterial)
- [编辑器模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial/Source/DynamicMaterialEditor)
- [纹理集模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial/Source/DynamicMaterialTextureSet)
- [着色器模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial/Source/DynamicMaterialShaders)