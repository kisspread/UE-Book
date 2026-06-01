# Motion Design - AvalanchePropertyAnimator

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计-属性动画器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、预设资源） |
| 模块 | `AvalanchePropertyAnimator` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalanchePropertyAnimator) | |

---

## 用途

AvalanchePropertyAnimator 是 Motion Design（运动设计）框架中的**属性动画模块**，专门用于对 Actor 和 Component 的各种属性进行动画驱动。

该模块解决的核心问题是：在虚拟制作和广播场景中，需要对场景中的元素（如 Text3D、几何体、材质参数等）进行**程序化的属性动画**，而不是依赖传统的 Skeletal Animation 或简单的 Timeline。它通过 Sequencer 集成，让用户可以在 Motion Design 工作流中创建、编辑和播放属性动画，实现复杂的视觉效果编排。

**典型应用场景**：
- 电视节目包装中的动态文字入场/退场动画
- 虚拟演播室中场景元素的动态变化
- 数据驱动的实时可视化展示
- 多画面合成中的元素动画同步

---

## 使用场景

- 你在做虚拟制作/广播项目，需要对 Text3D 的位置、旋转、缩放做关键帧动画 → 用 PropertyAnimator
- 你需要让多个对象的材质参数（如颜色、透明度）随时间变化 → 用 PropertyAnimator
- 你在 Motion Design 工作流中需要精确控制动画时序和缓动曲线 → 用 PropertyAnimator + Sequencer
- 你需要创建可重复使用的动画预设应用到不同对象上 → 用 PropertyAnimator 的模板系统

---

## 蓝图用法

### 核心节点

由于该模块主要服务于 Motion Design 编辑器工作流，公开的蓝图 API 相对有限。主要功能通过 Sequencer Track 和编辑器工具暴露。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetPropertyValue` | 设置属性动画的目标值 | `UAvaPropertyAnimatorBase` |
| `Play` | 播放属性动画 | `UAvaPropertyAnimatorBase` |
| `Stop` | 停止属性动画 | `UAvaPropertyAnimatorBase` |

### 使用示例（蓝图描述）

属性动画通常在 Motion Design 编辑器中通过以下步骤配置：

1. 在场景中选择目标 Actor
2. 通过 Motion Design 面板添加 PropertyAnimator 组件
3. 在属性列表中选择要动画化的属性
4. 在 Sequencer 中编辑关键帧
5. 设置缓动曲线和时间映射

---

## C++ 用法

### 头文件引入

```cpp
#include "AvaPropertyAnimatorBase.h"
#include "AvaPropertyAnimatorComponent.h"
```

### 基本用法

```cpp
// 创建属性动画器组件
UAvaPropertyAnimatorComponent* AnimatorComponent = 
    NewObject<UAvaPropertyAnimatorComponent>(TargetActor);
AnimatorComponent->RegisterComponent();

// 获取基础动画器
UAvaPropertyAnimatorBase* Animator = AnimatorComponent->GetPropertyAnimator();
if (Animator)
{
    // 配置动画参数
    Animator->SetDuration(2.0f);
    Animator->SetLoopCount(0); // 无限循环
    
    // 启动动画
    Animator->Play();
}
```

### 进阶用法

```cpp
// 自定义属性动画通道
UCLASS()
class UMyPropertyAnimatorChannel : public UAvaPropertyAnimatorChannelBase
{
    GENERATED_BODY()

public:
    // 覆写以实现自定义属性映射
    virtual bool IsPropertySupported(const FProperty* InProperty) const override;
    
    // 覆写以实现自定义插值逻辑
    virtual void ApplyPropertyValue(UObject* InObject, const FProperty* InProperty, 
                                     float InProgress) override;
};
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Sequencer` | 动画序列编辑和播放 |
| `PropertyAnimatorCore` | 属性动画核心框架 |
| `ActorModifierCore` | Actor 修改器核心 |
| `AvaCore` | Motion Design 核心框架 |

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-05-09 | `d53ec51b` | Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction | Motion Design 系列插件从实验性目录迁移到虚拟制作目录，标志正式发布 |

### 维护评价

- **状态**: 活跃维护
- **分析**:
  - 2025 年 5 月从 Experimental 迁移到 VirtualProduction，表明已通过 Epic 内部审核
  - 属于 Motion Design 大框架的一部分，该框架持续更新中
  - 与虚拟制作和广播工作流深度集成，是 Epic 重点发展方向
- **建议**: ✅ 可用于生产环境，特别是虚拟制作和广播项目

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalanchePropertyAnimator)
- [Motion Design 主插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [PropertyAnimatorCore 核心模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PropertyAnimatorCore)