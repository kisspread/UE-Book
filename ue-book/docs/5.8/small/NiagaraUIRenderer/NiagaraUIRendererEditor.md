# Niagara UI Renderer

> Renders Niagara CPU particle systems inside Slate/UMG widgets using a dedicated UI sprite renderer.

| 属性 | 值 |
|---|---|
| 分类 | FX |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `NiagaraUIRenderer` (Runtime), `NiagaraUIRendererEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraUIRenderer) | |

## 用途

NiagaraUIRenderer 解决了一个常见的 UI 特效需求：**在 UMG/Slate 界面中直接渲染 Niagara 粒子系统**。

传统上，Niagara 粒子只能在 3D 世界空间或 2D 精灵空间中渲染，无法直接嵌入到 UI 层级中。如果需要在 UI 上展示粒子效果（如技能图标特效、加载动画、UI 装饰粒子），开发者通常需要使用 Render Target 间接渲染或自行实现自定义 Slate 元素，流程复杂且性能不佳。

本插件提供了一个专用的 **UI Sprite Renderer**，让 Niagara CPU 粒子系统能够直接作为 UMG Widget 渲染在 UI 层中，粒子会自动参与 Slate 的布局和裁剪系统。

**关键限制**：仅支持 **CPU 粒子系统**，不支持 GPU 计算的粒子。

## 使用场景

- 你需要在技能按钮上添加发光粒子特效 → 用 NiagaraUIRenderer
- 你需要在 UI 上展示动态的加载/过渡动画粒子 → 用 NiagaraUIRenderer
- 你需要在 HUD 上叠加粒子装饰效果（如血迹飞溅、金币飘落） → 用 NiagaraUIRenderer
- 你需要粒子效果跟随 UI 元素移动并参与布局 → 用 NiagaraUIRenderer

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Niagara System` | 设置要渲染的 Niagara 粒子系统资产 | `UNiagaraUIWidget` |
| `Activate Niagara` | 激活粒子发射 | `UNiagaraUIWidget` |
| `Deactivate Niagara` | 停止粒子发射 | `UNiagaraUIWidget` |
| `Set Niagara Variable (Float)` | 设置 Niagara 系统中的浮点参数 | `UNiagaraUIWidget` |
| `Set Niagara Variable (Vector)` | 设置 Niagara 系统中的向量参数 | `UNiagaraUIWidget` |

### 使用示例

1. 在 UMG Widget Blueprint 中，从面板拖入 **Niagara UI Widget**（或在 Hierarchy 中添加）
2. 在 Details 面板中指定 **Niagara System Asset**（必须是 CPU 粒子系统）
3. 通过蓝图在运行时调用 `Activate Niagara` 启动粒子
4. 可通过 `Set Niagara Variable` 节点动态调整粒子参数（如颜色、速度、大小）

```
[Event BeginPlay] → [Activate Niagara]
[Button Clicked] → [Set Niagara Variable (Float) - "Intensity" = 2.0]
```

## C++ 用法

### 头文件引入

```cpp
#include "NiagaraUIWidget.h"
```

### 基本用法

```cpp
// 创建 Niagara UI Widget 并设置粒子系统
UNiagaraUIWidget* NiagaraWidget = NewObject<UNiagaraUIWidget>();
UNiagaraSystem* ParticleSystem = LoadObject<UNiagaraSystem>(nullptr, TEXT("/Game/FX/MyUIParticles"));
NiagaraWidget->SetNiagaraSystem(ParticleSystem);
NiagaraWidget->ActivateNiagara(true);
```

### 进阶用法

```cpp
// 动态修改 Niagara 参数
NiagaraWidget->SetNiagaraVariableFloat(FName("SpawnRate"), 100.0f);
NiagaraWidget->SetNiagaraVariableVector(FName("Color"), FVector(1.0f, 0.5f, 0.0f));
```

## Demo 示例

```cpp
// MyUIParticleWidget.h
#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "MyUIParticleWidget.generated.h"

class UNiagaraUIWidget;

UCLASS()
class UMyUIParticleWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    UPROPERTY(meta = (BindWidget))
    UNiagaraUIWidget* ParticleEffect;

    UPROPERTY(EditAnywhere, Category = "FX")
    UNiagaraSystem* NiagaraSystem;

protected:
    virtual void NativeConstruct() override;
};
```

```cpp
// MyUIParticleWidget.cpp
#include "MyUIParticleWidget.h"
#include "NiagaraUIWidget.h"

void UMyUIParticleWidget::NativeConstruct()
{
    Super::NativeConstruct();

    if (ParticleEffect && NiagaraSystem)
    {
        ParticleEffect->SetNiagaraSystem(NiagaraSystem);
        ParticleEffect->ActivateNiagara(true);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Niagara` | Niagara 粒子系统核心模块，提供粒子系统资产和运行时支持 |
| `NiagaraUIRenderer` | 本插件 Runtime 模块，提供 UI 粒子渲染能力 |

## 维护状态

### 近期更新

- 2026-04-06 `a55b12c5` - Add debug drawing to UI renderer
- 2026-04-02 `6697fae6` - Niagara UI Renderer plugin

### 维护评价

- **状态**：🆕 全新插件
- **实验性**：`IsExperimentalVersion=true`，表明该功能仍在实验阶段，API 可能发生变化
- **默认未启用**：`Installed=false`，需要手动在插件管理器中启用
- **依赖关系**：依赖 Niagara 插件，确保项目已启用 Niagara
- **推荐**：适合在实验性项目中尝试，生产环境使用需谨慎评估稳定性

⚠️ **注意**：该插件标记为实验性功能，未来版本可能会有 API 变更或功能调整。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraUIRenderer)
- [Niagara 官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/Niagara/)