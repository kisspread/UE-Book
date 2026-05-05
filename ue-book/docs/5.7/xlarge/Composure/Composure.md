# Composure

> Legacy system for real-time compositing. This plugin is no longer developed. Use Composure going forward.

| 属性 | 值 |
|---|---|
| 分类 | Compositing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、蓝图资产） |
| 模块 | `Composure` (Runtime), `ComposureEditor` (Runtime), `ComposureLayersEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-06-27 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/Composure) | |

---

## 用途

Composure 是 UE5 的**实时合成（Real-time Compositing）框架**，用于在引擎内将多个渲染层（Render Layers）实时合成到一起。它解决的核心问题是：**在不离开引擎的情况下，完成传统上需要 Nuke/After Effects 等外部合成软件才能完成的工作**。

具体来说，Composure 提供：

1. **节点式合成管线**：通过 `ACompositingElement` 构建输入→变换→输出的合成管线，每个元素可包含多个 Pass
2. **实时渲染层分离**：将 CG 场景、媒体输入、后处理效果等分离为独立层，再合成
3. **后处理集成**：内置 Bloom、Tonemapper、自定义材质等后处理 Pass
4. **媒体输入支持**：可将 MediaTexture 作为合成输入
5. **Sequencer 集成**：通过 MovieScene Track 实现合成参数的动画控制
6. **玩家视口输出**：将合成结果直接输出到玩家视口

**⚠️ 重要警告**：此插件标记为 **Legacy**，Epic 已声明不再开发此版本，建议使用新版 Composure。但截至 UE 5.7，此插件仍包含在引擎中。

---

## 使用场景

- 你需要在引擎内实时合成 CG 和实拍素材 → 用 Composure 的媒体输入 + CG 层合成
- 你在做虚拟制片（Virtual Production），需要实时预览合成效果 → 用 Composure 的玩家视口输出
- 你需要对渲染层应用独立的后处理（Bloom、色调映射等） → 用 Composure 的后处理 Pass
- 你需要在 Sequencer 中动画控制合成参数 → 用 Composure 的 MovieScene Track
- 你需要将合成结果输出到 MediaCapture → 用 `UCompositingMediaCaptureOutput`

---

## 核心概念

### 合成元素（Compositing Element）

`ACompositingElement` 是整个框架的核心类，代表一个合成节点。每个元素包含三类 Pass：

```
输入（Input）→ 变换/合成（Transform）→ 输出（Output）
```

- **Input**：数据源，如场景捕获、媒体纹理、其他合成元素的输出
- **Transform**：对输入进行处理，如材质变换、色调映射、Bloom
- **Output**：将结果输出到渲染目标、视口、媒体捕获等

### 继承式目标池（Inherited Target Pool）

`FInheritedTargetPool` 管理渲染目标的分配和回收，子元素从父元素继承目标池，实现资源复用。

### 纹理查找表（Texture Lookup Table）

`FCompositingTextureLookupTable` 维护一个名称→纹理的映射表，允许不同 Pass 之间通过名称引用彼此的输出。

---

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateComposureElement` | 创建新的合成元素 | `UComposureBlueprintLibrary` |
| `GetComposureElement` | 按名称获取合成元素 | `UComposureBlueprintLibrary` |
| `DeleteComposureElementAndChildren` | 删除合成元素及其子元素 | `UComposureBlueprintLibrary` |
| `CreatePlayerCompositingTarget` | 创建玩家合成目标 | `UComposureBlueprintLibrary` |
| `GetProjectionMatrixFromPostMoveSettings` | 从后移动设置获取投影矩阵 | `UComposureBlueprintLibrary` |
| `GetCroppingUVTransformationMatrixFromPostMoveSettings` | 获取裁剪 UV 变换矩阵 | `UComposureBlueprintLibrary` |
| `SetUVMapSettingsToMaterialParameters` | 将 UV 映射设置应用到材质参数 | `UComposureBlueprintLibrary` |
| `GetRedGreenUVFactorsFromChromaticAberration` | 从色差百分比获取 UV 因子 | `UComposureBlueprintLibrary` |
| `GetPlayerDisplayGamma` | 获取玩家显示 Gamma 值 | `UComposureBlueprintLibrary` |
| `CopyCameraSettingsToSceneCapture` | 复制相机设置到场景捕获 | `UComposureBlueprintLibrary` |
| `BloomToRenderTarget` | 执行 Bloom 并输出到渲染目标 | `UComposureLensBloomPass` |
| `TonemapToRenderTarget` | 执行色调映射并输出到渲染目标 | `UComposureTonemapperPass` |
| `Execute` | 执行后处理代理 | `UComposurePostProcessingPassProxy` |
| `SetMaterialInterface` | 设置材质 Pass 的材质 | `UCompositingElementMaterialPass` |
| `SetParameterMapping` | 设置材质参数与合成层的映射 | `UCompositingElementMaterialPass` |
| `EnqueueRendering` | 入队渲染请求 | `AComposurePipelineBaseActor` |
| `SetAutoRun` | 设置自动运行 | `AComposurePipelineBaseActor` |
| `SetRenderTarget` | 设置玩家渲染目标 | `UComposurePlayerCompositingTarget` |
| `SetPlayerCameraManager` | 设置玩家相机管理器 | `UComposurePlayerCompositingTarget` |

### 使用示例（蓝图描述）

**创建基本合成管线：**

1. 在关卡中放置 `ACompositingElement`（或其子类 `ACompositingCaptureBase`）
2. 在元素的 Details 面板中配置 Input Pass（如场景捕获）
3. 添加 Transform Pass（如材质变换、色调映射）
4. 添加 Output Pass（如渲染目标输出、玩家视口输出）
5. 设置 `bAutoRun = true` 使管线每帧自动执行

**蓝图中动态创建合成元素：**

1. 使用 `CreateComposureElement` 节点，指定元素名称和类类型
2. 使用返回的 `ACompositingElement` 引用配置其 Pass
3. 使用 `SetAutoRun` 控制是否自动运行

**将合成结果输出到玩家视口：**

1. 创建 `UComposurePlayerCompositingTarget`
2. 调用 `SetPlayerCameraManager` 绑定到玩家相机管理器
3. 调用 `SetRenderTarget` 设置渲染目标
4. 合成结果将自动替换玩家视口的渲染输出

---

## C++ 用法

### 头文件引入

```cpp
#include "CompositingElement.h"
#include "CompositingElements/CompositingElementPasses.h"
#include "CompositingElements/CompositingElementTransforms.h"
#include "CompositingElements/CompositingElementOutputs.h"
#include "CompositingElements/CompositingElementInputs.h"
#include "ComposureBlueprintLibrary.h"
#include "ComposurePostMoves.h"
#include "ComposureUVMap.h"
```

### 基本用法

**创建合成元素并配置 Pass：**

```cpp
// 创建一个合成元素
ACompositingElement* CompElement = UComposureBlueprintLibrary::CreateComposureElement(
    FName("MyCompElement"),
    ACompositingElement::StaticClass(),
    GetWorld()
);

// 设置自动运行
CompElement->SetAutoRun(true);
```

**使用后移动设置（Post Move Settings）：**

```cpp
// 来源: ComposurePostMoves.h
FComposurePostMoveSettings PostMoveSettings;
PostMoveSettings.Pivot = FVector2D(0.5, 0.5);
PostMoveSettings.Translation = FVector2D(0.1, 0.0);
PostMoveSettings.RotationAngle = 15.0f;
PostMoveSettings.Scale = 1.2f;

// 获取投影矩阵
FMatrix ProjMatrix = PostMoveSettings.GetProjectionMatrix(90.0f, 16.0f / 9.0f);

// 获取裁剪 UV 变换矩阵
FMatrix CropMatrix, UnCropMatrix;
PostMoveSettings.GetCroppingUVTransformationMatrix(16.0f / 9.0f, &CropMatrix, &UnCropMatrix);
```

**使用 UV 映射设置：**

```cpp
// 来源: ComposureUVMap.h
FComposureUVMapSettings UVMapSettings;
UVMapSettings.PreUVDisplacementMatrix = FMatrix::Identity;
UVMapSettings.PostUVDisplacementMatrix = FMatrix::Identity;
UVMapSettings.DisplacementDecodeParameters = FVector2D(1, 0);
UVMapSettings.DisplacementTexture = MyDisplacementTexture;

// 应用到材质实例
UMaterialInstanceDynamic* MID = /* ... */;
UVMapSettings.SetMaterialParameters(MID);

// 反转编码参数
FVector2D DecodeParams = FComposureUVMapSettings::InvertEncodingParameters(FVector2D(2.0, 0.5));
```

### 进阶用法

**自定义合成元素输入 Pass：**

```cpp
// 来源: CompositingElementInputs.h - UCompositingElementInput
UCLASS(BlueprintType, Blueprintable)
class UMyCustomInput : public UCompositingElementInput
{
    GENERATED_BODY()

public:
    virtual UTexture* GenerateInput_Implementation() override
    {
        // 返回你的自定义纹理
        return MyCustomTexture;
    }
};
```

**自定义合成元素变换 Pass：**

```cpp
// 来源: CompositingElementTransforms.h - UCompositingElementTransform
UCLASS(BlueprintType, Blueprintable)
class UMyCustomTransform : public UCompositingElementTransform
{
    GENERATED_BODY()

public:
    virtual UTexture* ApplyTransform_Implementation(
        UTexture* Input,
        UComposurePostProcessingPassProxy* PostProcessProxy,
        ACameraActor* TargetCamera) override
    {
        // 对输入纹理进行自定义变换
        // 返回变换后的纹理
        return TransformedTexture;
    }
};
```

**使用材质 Pass 进行合成：**

```cpp
// 来源: CompositingElementTransforms.h - UCompositingElementMaterialPass
UCompositingElementMaterialPass* MaterialPass = NewObject<UCompositingElementMaterialPass>();
MaterialPass->SetMaterialInterface(MyMaterial);

// 设置材质参数映射（将材质中的纹理参数映射到合成层名称）
MaterialPass->SetParameterMapping(FName("InputTexture"), FName("MyLayerName"));
```

**使用纹理查找表：**

```cpp
// 来源: CompositingTextureLookupTable.h
FCompositingTextureLookupTable LookupTable;

// 注册 Pass 结果
LookupTable.RegisterPassResult(FName("MyPass"), ResultTexture, 0x00);

// 查找命名的 Pass 结果
UTexture* FoundTexture = nullptr;
bool bFound = LookupTable.FindNamedPassResult(FName("MyPass"), FoundTexture);

// 链接嵌套查找表
FCompositingTextureLookupTable NestedTable;
LookupTable.LinkNestedSearchTable(FName("Nested"), &NestedTable);
```

**使用冻结帧控制器：**

```cpp
// 来源: CompFreezeFrameController.h
int32 FreezeFlags = 0;
FCompFreezeFrameController FreezeController(FreezeFlags);

// 锁定冻结帧
FFreezeFrameControlHandle LockKey = FreezeController.Lock();

// 设置冻结标志
FreezeController.SetFreezeFlags(ETargetUsageFlags::USAGE_Input, false, LockKey);

// 检查标志
bool bHasInput = FreezeController.HasAnyFlags(ETargetUsageFlags::USAGE_Input);

// 解锁
FreezeController.Unlock(LockKey);
```

---

## Demo 示例

### 自定义合成变换 Pass

```cpp
// MyCustomCompTransform.h
#pragma once

#include "CoreMinimal.h"
#include "CompositingElements/CompositingElementTransforms.h"
#include "MyCustomCompTransform.generated.h"

UCLASS(BlueprintType, Blueprintable, meta=(DisplayName="My Custom Transform"))
class MYPROJECT_API UMyCustomCompTransform : public UCompositingElementTransform
{
    GENERATED_BODY()

public:
    /** 自定义强度参数 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Compositing Pass")
    float Intensity = 1.0f;

    /** 自定义颜色 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Compositing Pass")
    FLinearColor TintColor = FLinearColor::White;

protected:
    virtual UTexture* ApplyTransform_Implementation(
        UTexture* Input,
        UComposurePostProcessingPassProxy* PostProcessProxy,
        ACameraActor* TargetCamera) override;
};
```

```cpp
// MyCustomCompTransform.cpp
#include "MyCustomCompTransform.h"
#include "ComposurePostProcessingPassProxy.h"
#include "Engine/TextureRenderTarget2D.h"

UTexture* UMyCustomCompTransform::ApplyTransform_Implementation(
    UTexture* Input,
    UComposurePostProcessingPassProxy* PostProcessProxy,
    ACameraActor* TargetCamera)
{
    if (!Input)
    {
        return nullptr;
    }

    // 请求一个渲染目标
    UTextureRenderTarget2D* OutputTarget = RequestNativelyFormattedTarget();
    if (!OutputTarget)
    {
        return nullptr;
    }

    // 在这里执行你的自定义合成逻辑
    // 例如：使用后处理代理执行材质变换
    // PostProcessProxy->Execute(Input, MyPassPolicy);

    return OutputTarget;
}
```

### 自定义合成元素输入 Pass

```cpp
// MyCustomCompInput.h
#pragma once

#include "CoreMinimal.h"
#include "CompositingElements/CompositingElementInputs.h"
#include "MyCustomCompInput.generated.h"

class UTexture2D;

UCLASS(BlueprintType, Blueprintable, meta=(DisplayName="My Custom Input"))
class MYPROJECT_API UMyCustomCompInput : public UCompositingElementInput
{
    GENERATED_BODY()

public:
    /** 输入纹理 */
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Compositing Pass")
    TObjectPtr<UTexture2D> InputTexture;

protected:
    virtual UTexture* GenerateInput_Implementation() override
    {
        return InputTexture;
    }
};
```

---

## 模块依赖

从 Build.cs 分析，Composure 插件的模块依赖如下：

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 媒体纹理和媒体输入支持 |
| `MediaUtils` | 媒体工具函数 |
| `MovieScene` | Sequencer 集成（MovieScene Track） |
| `MovieSceneTracks` | Sequencer 轨道支持 |
| `LevelSequence` | 关卡序列支持 |
| `OpenColorIO` | OCIO 色彩空间转换 |
| `CameraCalibrationCore` | 镜头畸变校准（CG 层使用） |

无特殊依赖（仅标准 Core/Engine/Slate 等）的部分已省略。

---

## 维护状态

### 近期更新

```
- c4c3894de032 Fix or silence false positive PVS warnings in 7.36
- a492f271b78f Fix missing virtual destructor after the base interface class had its own removed
- bd6f24cfa8a4 Reinstate change type propagation when sending property change events up the chain, allowing Interactive editor changes to work on properties in nested arrays - Previously, the change type was changed to Unspecified to prevent ArrayAdd events on nested arrays from being interpreted as adds - Resolved the offending case by swapping `ACompositingElement::PostEditChangeProperty` to `ACompositingElement::PostEditChangeChainProperty` and checking that there are no nested containers further down the property chain
```

- `c4c3894de032` — 修复 PVS 静态分析工具的误报警告，属于代码质量维护
- `a492f271b78f` — 修复虚析构函数缺失问题，属于编译兼容性修复
- `bd6f24cfa8a4` — 修复编辑器中嵌套数组属性变更事件的传播问题，属于功能性 bug 修复

### 维护评价

**⚠️ 此插件已标记为 Legacy，不再积极开发。**

- **创建时间**：2017 年，已有约 8 年历史
- **维护状态**：近期更新均为编译修复和 bug 修复，无新功能开发
- **官方声明**：.uplugin Description 明确表示 "This plugin is no longer developed"
- **默认禁用**：`EnabledByDefault = false`，需要手动启用
- **替代方案**：Epic 建议使用新版 Composure（位于同级目录或其他位置）

**建议**：
- 如果是新项目，**不建议使用此 Legacy 版本**，应寻找新版 Composure
- 如果已有项目依赖此插件，短期内仍可使用，但需注意未来版本可能移除
- 此插件功能完整，包含 209 个源文件，覆盖了实时合成的完整工作流

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/Composure)
- 官方文档：无（.uplugin 中 DocsURL 为空）

---

## 子模块文档

由于此插件规模较大（209 个源文件），以下为各子模块的详细文档：

- [CompositingElement — 合成元素核心](./CompositingElement.md)
- [合成 Pass 系统（Input/Transform/Output）](./CompositingPasses.md)
- [后处理管线（Bloom/Tonemapper/材质）](./PostProcessing.md)
- [Sequencer 集成与导出](./SequencerIntegration.md)
- [工具类与编辑器支持](./Utilities.md)