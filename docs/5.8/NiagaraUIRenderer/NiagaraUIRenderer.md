# Niagara UI Renderer

> Renders Niagara CPU particle systems inside Slate/UMG widgets using a dedicated UI sprite renderer.

| 属性 | 值 |
|---|---|
| 分类 | FX |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `NiagaraUIRenderer` (Runtime), `NiagaraUIRendererEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraUIRenderer) | |

## 用途

NiagaraUIRenderer 解决了一个常见但棘手的问题：**如何在 UMG/Slate UI 界面中直接渲染 Niagara 粒子特效**。

传统上，Niagara 粒子系统只能在 3D 世界空间中渲染。如果想在 UI 上叠加粒子效果（如技能冷却闪光、背包物品发光、菜单装饰粒子），开发者通常需要使用 Scene Capture 2D 捕获 3D 粒子再贴到 UI 上，或者用 Render Target 做中转——这些方案既笨重又消耗性能。

本插件提供了一条专用路径：通过自定义的 **UI Sprite Renderer**，将 Niagara CPU 粒子的模拟数据直接转换为 Slate 顶点，由 Slate 渲染管线绘制到 UI 层。粒子的位置通过世界坐标到屏幕坐标的投影变换（支持 XY/XZ/YZ 三种平面映射），最终以 Slate 绘制元素的形式输出，完全绕过了 3D 渲染管线。

**核心设计思路**：
- `UNiagaraUIComponent` 继承自 `UNiagaraComponent`，在 Tick 中收集粒子模拟数据并打包为 `FNiagaraUIRenderData`
- `UNiagaraUISpriteRendererProperties` 作为 Niagara 渲染器属性，负责将粒子数据（位置、颜色、大小、旋转、SubUV 索引等）转换为 Slate 顶点
- `SNiagaraUIWidget`（Slate 层）在 `OnPaint` 中通过 `FNiagaraUISlateRenderContext` 将顶点提交给 Slate 绘制
- `UNiagaraUIWidget`（UMG 层）封装了 Slate Widget，暴露蓝图友好的属性和接口

## 使用场景

- 你在做一个 RPG 游戏，需要在技能图标上播放粒子特效（冷却闪光、激活光环）→ 用 NiagaraUIRenderer
- 你需要在主菜单/暂停菜单上添加装饰性粒子效果（飘落的雪花、飞舞的萤火虫）→ 用 NiagaraUIRenderer
- 你想在 HUD 上显示带有粒子效果的血条/能量条 → 用 NiagaraUIRenderer
- 你需要在背包/商店 UI 中为物品添加发光、旋转等粒子装饰 → 用 NiagaraUIRenderer

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetDesiredWidgetSize` | 设置 Widget 的期望尺寸（影响布局，不影响粒子坐标映射） | `UNiagaraUIWidget` |

### 核心属性（蓝图可读写）

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `DesiredWidgetSize` | `FVector2D` | Widget 的布局尺寸，默认 (100, 100) | `UNiagaraUIWidget` |
| `WorldToScreenScale` | `float` | 世界坐标到屏幕坐标的缩放比例，默认 1.0 | `UNiagaraUIWidget` |
| `WorldToScreenPlane` | `ENiagaraUIScreenPlane` | 投影平面选择：XY / XZ / YZ | `UNiagaraUIWidget` |
| `HorizontalAlignment` | `EHorizontalAlignment` | 世界原点在 Widget 中的水平对齐方式 | `UNiagaraUIWidget` |
| `VerticalAlignment` | `EVerticalAlignment` | 世界原点在 Widget 中的垂直对齐方式 | `UNiagaraUIWidget` |
| `NiagaraSystem` | `UNiagaraSystem*` | 要渲染的 Niagara 系统资产 | `UNiagaraUIWidget` |

### 使用示例（蓝图描述）

**基本用法**：
1. 在 UMG Widget Blueprint 中，从面板拖入 **Niagara UI Widget**
2. 在 Details 面板中设置 `Niagara System` 为你的 Niagara 粒子资产
3. 调整 `Desired Widget Size` 控制 Widget 在布局中的大小
4. 调整 `World To Screen Scale` 控制粒子在 UI 中的显示大小
5. 选择 `World To Screen Plane`（通常 2D 粒子用 XY，3D 粒子用 XZ）

**动态调整**：
- 在蓝图中获取 Niagara UI Widget 引用，调用 `Set Desired Widget Size` 动态改变尺寸
- 通过设置 `World To Screen Scale` 可实现粒子的缩放动画效果

## C++ 用法

### 头文件引入

```cpp
#include "NiagaraUIWidget.h"
#include "NiagaraUIComponent.h"
#include "NiagaraUISpriteRendererProperties.h"
#include "NiagaraUIRenderContext.h"
```

### 基本用法

创建并配置 Niagara UI Widget：

```cpp
// 在 C++ 中创建 UMG Widget 并设置 Niagara 系统
UNiagaraUIWidget* NiagaraWidget = NewObject<UNiagaraUIWidget>(this);
NiagaraWidget->SetDesiredWidgetSize(FVector2D(200.0, 200.0));

// 通过蓝图可读写属性直接设置
// （通常在 UMG 设计器中完成，C++ 中较少直接操作）
```

### 进阶用法

**自定义渲染上下文参数**：

`FNiagaraUIRenderContext` 提供了精细的渲染控制：

```cpp
// 渲染上下文支持的配置：
// - SetLayerId()          : 设置绘制层级
// - SetDrawEffect()       : 设置绘制效果（如半透明、模糊等）
// - SetScreenParameters() : 设置投影平面
// - SetScreenOrigin()     : 设置屏幕原点
// - SetScreenOriginAlignment() : 通过水平/垂直对齐设置原点
// - SetScreenScale()      : 设置缩放比例

// 坐标转换示例
// PositionToScreen() 将 Niagara 世界坐标转换为 Widget 屏幕坐标
// SizeToScreen() 将世界尺寸转换为屏幕尺寸
```

**自定义渲染器属性**：

`UNiagaraUISpriteRendererProperties` 暴露了粒子到 Slate 顶点的绑定：

```cpp
// 可绑定的粒子属性：
// - PositionBinding              : 粒子位置
// - ColorBinding                 : 粒子颜色
// - SpriteSizeBinding            : 精灵大小
// - SpriteRotationBinding        : 精灵旋转
// - SubImageIndexBinding         : SubUV 帧索引
// - DynamicMaterialParameterBinding : 动态材质参数
// - CustomSortingBinding         : 自定义排序值
// - RendererVisibilityTagBinding : 渲染可见性标签
```

## Demo 示例

### 自定义 Niagara UI Widget 子类

```cpp
// MyNiagaraUIWidget.h
#pragma once

#include "CoreMinimal.h"
#include "NiagaraUIWidget.h"
#include "MyNiagaraUIWidget.generated.h"

UCLASS()
class UMyNiagaraUIWidget : public UNiagaraUIWidget
{
    GENERATED_BODY()

public:
    // 动态调整粒子缩放
    UFUNCTION(BlueprintCallable, Category = "Niagara")
    void SetParticleScale(float InScale);

    // 切换投影平面
    UFUNCTION(BlueprintCallable, Category = "Niagara")
    void SetProjectionPlane(ENiagaraUIScreenPlane InPlane);
};
```

```cpp
// MyNiagaraUIWidget.cpp
#include "MyNiagaraUIWidget.h"

void UMyNiagaraUIWidget::SetParticleScale(float InScale)
{
    WorldToScreenScale = InScale;
    // SynchronizeProperties 会在下一帧自动调用
}

void UMyNiagaraUIWidget::SetProjectionPlane(ENiagaraUIScreenPlane InPlane)
{
    WorldToScreenPlane = InPlane;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Niagara` | Niagara 粒子系统核心模块（插件级依赖） |

无其他特殊依赖（仅标准 Core/Engine/Slate/UMG 等）。

## 维护状态

### 近期更新

- 2026-04-06 `a55b12c5` - Add debug drawing to UI renderer
- 2026-04-02 `6697fae6` - Niagara UI Renderer plugin

### 维护评价

- **实验性插件**：`.uplugin` 中 `IsExperimentalVersion=true`，`Installed=false`，表明该插件仍处于实验阶段，尚未默认安装
- **依赖 Niagara**：作为 Niagara 的 UI 扩展，需要 Niagara 插件启用才能工作
- **CPU 粒子限制**：仅支持 CPU 粒子模拟，不支持 GPU 粒子（从 `FNiagaraUIRenderContext` 使用 `FNiagaraDataBufferRef` 读取 CPU 数据可推断）
- **仅 Sprite 渲染器**：当前仅实现了 `UNiagaraUISpriteRendererProperties`（UI Sprite Renderer），不支持 Mesh/ Ribbon 等其他渲染器类型
- **⚠️ 实验性警告**：该插件标记为实验性，API 可能在未来版本中发生变化，不建议在生产环境中使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraUIRenderer)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraUIRenderer/Tests)（如果存在）