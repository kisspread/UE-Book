# Material Designer

> Compact dynamic material creator and editor, similar in style to other DDCs.

| 属性 | 值 |
|---|---|
| 中文名 | 材质设计器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `DynamicMaterial` (Runtime), `DynamicMaterialTextureSet` (Runtime), `DynamicMaterialEditor` (Editor), `DynamicMaterialTextureSetEditor` (Editor), `DynamicMaterialShaders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DynamicMaterial) | |

## 用途

Material Designer 提供了一套**模型驱动**的材质创建与编辑系统。与传统节点式材质编辑器不同，它通过组件化层级结构（Component Hierarchy）来定义材质：

- **程序化材质构建**：将材质属性（BaseColor、Roughness、Normal 等）组织为 `UDMMaterialValue` 组件，通过模型（`UDynamicMaterialModel`）自动生成 `UMaterial` 资产
- **运行时动态修改**：通过 `UDynamicMaterialModelDynamic` 和对应的 Dynamic Value 实例，在运行时通过 MID（Material Instance Dynamic）修改材质参数
- **渲染目标纹理**：内置文本渲染器（`UDMRenderTargetTextRenderer`）和 UMG 控件渲染器（`UDMRenderTargetUMGWidgetRenderer`），可将 UI 内容渲染为纹理用于材质
- **参数暴露与动画**：支持将材质参数暴露为 Sequencer 可关键帧属性，适配 Virtual Production 动画流程

该插件最初位于 `Engine/Plugins/Experimental`，后迁移至 `Engine/Plugins/VirtualProduction`，是 Motion Design 工具链的核心材质模块。

## 使用场景

- 你在做 Motion Design 项目，需要程序化创建和修改材质 → 用 Material Designer 的 Model/Value 体系
- 你需要在运行时动态切换材质纹理、颜色、UV 参数 → 用 `UDynamicMaterialModelDynamic` + Dynamic Value
- 你想把文本或 UI 控件渲染为材质纹理（如动态标签、信息面板）→ 用 `UDMRenderTargetTextRenderer`
- 你需要一个轻量级材质编辑器供非技术美术使用 → Material Designer 的组件化编辑界面
- 你要在 Sequencer 中对材质参数做关键帧动画 → 参数暴露（`SetShouldExposeParameter`）+ Sequencer 集成

## 蓝图用法

### 模型管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsModelValid` | 检查模型是否有效且未被销毁 | `UDynamicMaterialModel` |
| `GetMaterialModel` | 从 Material Instance 解析获取底层模型 | `UDynamicMaterialInstance` |
| `GetMaterialModelBase` | 获取 Material Instance 关联的模型基类 | `UDynamicMaterialInstance` |
| `GetGeneratedMaterial` | 获取模型生成的 UMaterial 资产 | `UDynamicMaterialModel` |
| `GetComponentByPath` | 通过路径字符串查找模型中的组件 | `UDynamicMaterialModel` |
| `AddValue` | 创建新的材质值组件并添加到模型 | `UDynamicMaterialModel` |
| `HasParameterName` | 检查指定参数名是否已被占用 | `UDynamicMaterialModel` |

### 全局参数访问

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetGlobalParameterValueForMaterialProperty` | 根据材质属性类型获取全局参数值（如 BaseColor、Opacity） | `UDynamicMaterialModel` |
| `GetGlobalParameterValue` | 根据 FName 获取全局参数值 | `UDynamicMaterialModel` |

### 材质值操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateMaterialValue` | 静态工厂方法，创建指定类型的材质值 | `UDMMaterialValue` |
| `GetValue` / `SetValue` | 获取/设置具体值（各子类实现） | `UDMMaterialValueFloat1` 等 |
| `GetMaterialParameterName` | 获取参数名（自动生成或手动设置） | `UDMMaterialValue` |
| `SetParameterName` | 设置自定义参数名，覆盖自动生成的名称 | `UDMMaterialValue` |
| `SetShouldExposeParameter` | 控制参数是否暴露到材质实例供外部修改 | `UDMMaterialValue` |
| `IsLocal` | 判断值是局部值还是全局值 | `UDMMaterialValue` |

### 纹理 UV 控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetOffset` / `GetOffset` | 设置/获取 UV 偏移 | `UDMTextureUV` |
| `SetTiling` / `GetTiling` | 设置/获取 UV 平铺 | `UDMTextureUV` |
| `SetRotation` / `GetRotation` | 设置/获取 UV 旋转角度 | `UDMTextureUV` |
| `SetPivot` / `GetPivot` | 设置/获取旋转/平铺的中心点 | `UDMTextureUV` |

### 动态实例（运行时）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create` | 基于父模型创建动态模型实例 | `UDynamicMaterialModelDynamic` |
| `GetParentModel` | 获取父模型引用 | `UDynamicMaterialModelDynamic` |
| `GetComponentDynamic` | 按名称获取动态组件 | `UDynamicMaterialModelDynamic` |
| `ToEditable` | 将动态实例转换为可编辑模型 | `UDynamicMaterialModelDynamic` |

### 渲染目标

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateRenderTargetRenderer` | 静态工厂方法，创建渲染目标渲染器 | `UDMRenderTargetRenderer` |
| `UpdateRenderTarget` | 同步更新渲染目标内容 | `UDMRenderTargetRenderer` |
| `AsyncUpdateRenderTarget` | 异步更新渲染目标（帧末执行） | `UDMRenderTargetRenderer` |
| `SetText` / `GetText` | 设置/获取文本渲染器的文本内容 | `UDMRenderTargetTextRenderer` |
| `SetFontInfo` | 设置文本字体 | `UDMRenderTargetTextRenderer` |
| `SetTextColor` | 设置文本颜色 | `UDMRenderTargetTextRenderer` |

### 组件基础操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsComponentValid` | 检查组件是否有效 | `UDMMaterialComponent` |
| `Update` | 触发组件及其父级的更新链 | `UDMMaterialComponent` |
| `GetComponentPath` | 获取组件从模型到自身的完整路径 | `UDMMaterialComponent` |
| `GetParentComponent` | 获取模型层级中的父组件 | `UDMMaterialComponent` |
| `SetComponentState` | 设置组件生命周期状态 | `UDMMaterialComponent` |

### 蓝图使用示例

**创建材质模型并修改全局颜色**：
1. 创建 `UDynamicMaterialModel` 对象（或从已有的 Material Designer Material 中获取）
2. 调用 `GetGlobalParameterValueForMaterialProperty(EmissiveColor)` 获取发光颜色值
3. 将返回值 Cast 为 `UDMMaterialValueFloat3RGB`
4. 调用 `SetValue(FLinearColor::Red)` 设置颜色

**创建动态实例并运行时修改参数**：
1. 获取已有的 `UDynamicMaterialModel` 引用
2. 调用 `UDynamicMaterialModelDynamic::Create(Outer, ParentModel)` 创建动态实例
3. 通过 `GetComponentDynamic("参数名")` 获取目标动态值
4. Cast 后调用 `SetValue()` 修改运行时值

## C++ 用法

### 头文件引入

```cpp
// 核心模型与组件
#include "Model/DynamicMaterialModel.h"
#include "Model/DynamicMaterialModelDynamic.h"
#include "Material/DynamicMaterialInstance.h"
#include "Components/DMMaterialComponent.h"
#include "Components/DMMaterialValue.h"

// 具体值类型
#include "Components/MaterialValues/DMMaterialValueFloat1.h"
#include "Components/MaterialValues/DMMaterialValueFloat3RGB.h"
#include "Components/MaterialValues/DMMaterialValueTexture.h"

// 纹理 UV
#include "Components/DMTextureUV.h"

// 渲染目标
#include "Components/MaterialValues/DMMaterialValueRenderTarget.h"
#include "Components/RenderTargetRenderers/DMRenderTargetTextRenderer.h"

// 定义与枚举
#include "DMDefs.h"
```

### 基本用法 — 创建材质值并设置参数

```cpp
// 基于 DMDefs.h 和 DMMaterialValue.h 的 API

// 创建一个浮点材质值
UDMMaterialValueFloat1* FloatValue = Cast<UDMMaterialValueFloat1>(
    UDMMaterialValue::CreateMaterialValue(
        MaterialModel,
        TEXT("MyFloatParam"),
        UDMMaterialValueFloat1::StaticClass(),
        false  // false = 全局值, true = 局部值
    )
);

// 设置参数名（可选，不设置则自动生成）
FloatValue->SetParameterName(FName("Custom_FloatParam"));

// 设置值
FloatValue->SetValue(0.75f);

// 暴露参数到材质实例（可在外部/MID中修改）
FloatValue->SetShouldExposeParameter(true);
```

### 基本用法 — 纹理 UV 控制

```cpp
// 基于 DMTextureUV.h 的 API

// 创建纹理 UV
UDMTextureUV* TextureUV = UDMTextureUV::CreateTextureUV(OuterObject);

// 配置 UV 参数
TextureUV->SetOffset(FVector2D(0.1f, 0.2f));
TextureUV->SetTiling(FVector2D(2.0f, 2.0f));
TextureUV->SetRotation(45.0f);
TextureUV->SetPivot(FVector2D(0.5f, 0.5f));

// 将 UV 参数应用到 MID
TextureUV->SetMIDParameters(MyMID);
```

### 进阶用法 — 动态模型实例

```cpp
// 基于 DynamicMaterialModelDynamic.h 的 API

// 假设已有父模型 ParentModel (UDynamicMaterialModel*)
UDynamicMaterialModelDynamic* DynamicModel = UDynamicMaterialModelDynamic::Create(
    GetTransientPackage(),  // 或任何合适的 Outer
    ParentModel
);

// 确保所有父模型组件已同步到动态实例
DynamicModel->EnsureComponents();

// 获取动态值并修改
UDMMaterialValueFloat3RGBDynamic* ColorDynamic = Cast<UDMMaterialValueFloat3RGBDynamic>(
    DynamicModel->GetComponentDynamic(FName("BaseColorValue"))
);
if (ColorDynamic)
{
    ColorDynamic->SetValue(FLinearColor(1.0f, 0.0f, 0.0f, 1.0f));
}

// 应用到 MID
UMaterialInstanceDynamic* MID = /* 获取或创建 MID */;
DynamicModel->ApplyComponents(MID);

// 订阅值更新回调
DynamicModel->GetOnValueDynamicUpdateDelegate().AddLambda(
    [](UDMMaterialValueDynamic* ChangedValue) {
        // 响应值变化
    }
);

// 转换为可编辑模型（保存快照）
UDynamicMaterialModel* EditableModel = DynamicModel->ToEditable(GetTransientPackage());
```

### 进阶用法 — 渲染目标文本纹理

```cpp
// 基于 DMMaterialValueRenderTarget.h 和 DMRenderTargetTextRenderer.h

// 创建渲染目标材质值
UDMMaterialValueRenderTarget* RTValue = /* 从模型获取或创建 */;

// 配置渲染目标
RTValue->SetTextureSize(FIntPoint(512, 256));
RTValue->SetTextureFormat(RTF_RGBA8);
RTValue->SetClearColor(FLinearColor::Transparent);

// 创建文本渲染器
UDMRenderTargetTextRenderer* TextRenderer = Cast<UDMRenderTargetTextRenderer>(
    UDMRenderTargetRenderer::CreateRenderTargetRenderer(
        UDMRenderTargetTextRenderer::StaticClass(),
        RTValue
    )
);

// 配置文本
TextRenderer->SetText(FText::FromString(TEXT("Hello Material Designer")));
TextRenderer->SetTextColor(FLinearColor::White);
TextRenderer->SetBackgroundColor(FLinearColor(0.1f, 0.1f, 0.1f, 1.0f));
TextRenderer->SetFontInfo(FSlateFontInfo(FPaths::EngineContentDir() / TEXT("Slate/Fonts/Roboto-Bold.ttf"), 24));

// 异步更新渲染目标
TextRenderer->AsyncUpdateRenderTarget();
```

## Demo 示例

```cpp
// MaterialDesignerDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MaterialDesignerDemo.generated.h"

class UDynamicMaterialModel;
class UDynamicMaterialInstance;
class UDMMaterialValueFloat1;
class UDMMaterialValueFloat3RGB;

UCLASS()
class AMaterialDesignerDemo : public AActor
{
    GENERATED_BODY()

public:
    AMaterialDesignerDemo();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(EditAnywhere, Category = "Demo")
    float AnimSpeed = 1.0f;

protected:
    UPROPERTY()
    TObjectPtr<UDynamicMaterialModel> MaterialModel;

    UPROPERTY()
    TObjectPtr<UDynamicMaterialInstance> MaterialInstance;

    UPROPERTY()
    TObjectPtr<UDMMaterialValueFloat1> RoughnessValue;

    UPROPERTY()
    TObjectPtr<UDMMaterialValueFloat3RGB> EmissiveColorValue;

private:
    float ElapsedTime = 0.0f;
};
```

```cpp
// MaterialDesignerDemo.cpp
#include "MaterialDesignerDemo.h"

#include "Model/DynamicMaterialModel.h"
#include "Material/DynamicMaterialInstance.h"
#include "Components/DMMaterialValue.h"
#include "Components/MaterialValues/DMMaterialValueFloat1.h"
#include "Components/MaterialValues/DMMaterialValueFloat3RGB.h"
#include "Components/DMTextureUV.h"
#include "DMDefs.h"

AMaterialDesignerDemo::AMaterialDesignerDemo()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建可视化组件
    UStaticMeshComponent* MeshComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComp;
    static ConstructorHelpers::FObjectFinder<UStaticMesh> MeshAsset(
        TEXT("/Engine/BasicShapes/Cube.Cube"));
    if (MeshAsset.Succeeded())
    {
        MeshComp->SetStaticMesh(MeshAsset.Object);
    }
}

void AMaterialDesignerDemo::BeginPlay()
{
    Super::BeginPlay();

    // --- 创建材质模型 ---
    // 注：实际使用中通常通过 UDynamicMaterialModelFactory 或编辑器创建
    // 这里演示 API 调用流程

    // 创建浮点值 (粗糙度)
    RoughnessValue = Cast<UDMMaterialValueFloat1>(
        UDMMaterialValue::CreateMaterialValue(
            MaterialModel,
            TEXT("DemoRoughness"),
            UDMMaterialValueFloat1::StaticClass(),
            false  // 全局值
        )
    );
    if (RoughnessValue)
    {
        RoughnessValue->SetParameterName(FName("Demo_Roughness"));
        RoughnessValue->SetShouldExposeParameter(true);
        RoughnessValue->SetValue(0.5f);
    }

    // 创建颜色值 (自发光)
    EmissiveColorValue = Cast<UDMMaterialValueFloat3RGB>(
        UDMMaterialValue::CreateMaterialValue(
            MaterialModel,
            TEXT("DemoEmissive"),
            UDMMaterialValueFloat3RGB::StaticClass(),
            false
        )
    );
    if (EmissiveColorValue)
    {
        EmissiveColorValue->SetParameterName(FName("Demo_EmissiveColor"));
        EmissiveColorValue->SetShouldExposeParameter(true);
        EmissiveColorValue->SetValue(FLinearColor(0.0f, 0.5f, 1.0f));
    }

    // 订阅值更新
    if (MaterialModel)
    {
        MaterialModel->GetOnValueUpdateDelegate().AddLambda(
            [](UDMMaterialValue* ChangedValue, EDMUpdateType UpdateType)
            {
                UE_LOG(LogTemp, Log, TEXT("Material value updated: %s"),
                    *ChangedValue->GetMaterialParameterName().ToString());
            }
        );

        // 获取生成的材质并应用到 Mesh
        UMaterial* GeneratedMat = MaterialModel->GetGeneratedMaterial();
        if (GeneratedMat)
        {
            UStaticMeshComponent* MeshComp = Cast<UStaticMeshComponent>(RootComponent);
            if (MeshComp)
            {
                MeshComp->SetMaterial(0, GeneratedMat);
            }
        }
    }
}

void AMaterialDesignerDemo::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    ElapsedTime += DeltaTime * AnimSpeed;

    // 动态修改粗糙度（正弦波动画）
    if (RoughnessValue)
    {
        float NewRoughness = FMath::Lerp(0.1f, 0.9f, (FMath::Sin(ElapsedTime) + 1.0f) * 0.5f);
        RoughnessValue->SetValue(NewRoughness);
    }

    // 动态修改自发光颜色（颜色循环）
    if (EmissiveColorValue)
    {
        FLinearColor NewColor = FLinearColor::MakeFromHSV8(
            FMath::Fmod(ElapsedTime * 30.0f, 360.0f), 255, 255);
        EmissiveColorValue->SetValue(NewColor);
    }
}
```

## 模块依赖

从源码分析，以下为该插件的独特依赖（Core/Engine/Slate/UMG 等标准依赖已省略）：

| 模块 | 用途 |
|---|---|
| `CustomDetailsView` | 自定义详情面板 UI（编辑器模块依赖，提供属性编辑界面） |
| `JsonUtilities` | JSON 序列化/反序列化支持（IDMJsonSerializable 接口） |
| `RenderCore` | 渲染目标纹理管理 |

> 该插件还依赖 `DynamicMaterialTextureSet`（纹理集合运行时模块）和 `DynamicMaterialShaders`（自定义着色器），均为插件内部模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 编辑器标签页移至独立分组 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/断开通知机制 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退 CL53913857 的变更 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/断开通知机制（重提交） |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |

### 维护评价

- **活跃维护**：最近更新集中在 2026 年 5 月，更新频率高，几乎每日有提交
- **Motion Design 生态核心**：该插件是 Motion Design / Virtual Production 工具链的组成部分，随整体框架一起维护
- **近期改动方向**：主要是视口重构和编译警告修复等基础设施维护，插件自身功能稳定
- **来源**：2025 年 5 月从 `Engine/Plugins/Experimental` 迁移至 `Engine/Plugins/VirtualProduction`，说明已被正式纳入 Virtual Production 工具链
- **代码规模**：649 个源文件，属于大型插件，架构设计成熟（组件化层级、接口抽象、JSON 序列化、动态实例化）
- **已知注意事项**：部分旧 API 标记为 `UE_DEPRECATED(5.3)` 或 `UE_DEPRECATED(5.5)`，说明有持续重构
- **推荐使用**：✅ 如果你在做 Motion Design 或 Virtual Production 项目，这是官方推荐的程序化材质方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DynamicMaterial)
- [CustomDetailsView 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CustomDetailsView)（依赖项）