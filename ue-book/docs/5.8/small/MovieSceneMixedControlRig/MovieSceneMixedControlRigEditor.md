# Sequencer Mixed Control Rig

> System for using the Anim Mixer to mix control rig tracks

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MovieSceneMixedControlRig` (Runtime), `MovieSceneMixedControlRigEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-31 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieSceneMixedControlRig) | |

## 用途

该插件为 Sequencer 中的 **Control Rig 动画轨道** 提供了与 **Anim Mixer（动画混合器）** 的集成能力。

在标准工作流中，Sequencer 的 Anim Mixer 可以混合普通的动画轨道，但 Control Rig 轨道由于其程序化控制的特殊性，无法直接参与混合。本插件通过实现 `IMovieSceneAnimMixerBakeProvider` 和 `IMovieSceneEditingContextLayerResolver` 两个接口，解决了以下问题：

1. **混合层解析**：将 Sequencer 的编辑上下文（Editing Context）正确映射到 Anim Mixer 的混合层，使 Control Rig 轨道能被 Mixer 识别和处理。
2. **烘焙支持**：提供将混合结果烘焙回 Control Rig 的能力，烘焙完成后自动激活 Control Rig 编辑模式以便进一步调整。

简而言之，这个插件让你能在 Sequencer 中像混合普通动画一样混合 Control Rig 轨道。

## 使用场景

- 你在 Sequencer 中使用 Control Rig 做面部动画，需要将多条 Control Rig 轨道的动画混合在一起 → 启用此插件，在 Anim Mixer 中混合 Control Rig 轨道
- 你有一段通过 Control Rig 驱动的身体动画和一段关键帧动画，需要平滑过渡混合 → 使用此插件将两者在 Mixer 中混合后烘焙为最终结果
- 你需要在 Sequencer 中对 Control Rig 动画做 A/B 对比或层叠混合 → 通过 Anim Mixer 的混合功能实现

## 蓝图用法

本插件主要通过 Sequencer 编辑器 UI 操作，不暴露蓝图节点。其功能通过 Sequencer 的 Anim Mixer 面板和右键菜单中的"Bake to Control Rig"选项触发。

### 核心操作流程

1. 在 Sequencer 中添加 Control Rig 轨道
2. 打开 Anim Mixer 面板
3. 将 Control Rig 轨道添加到混合层
4. 调整混合权重
5. 右键选择 **Bake to Control Rig** 将混合结果烘焙回 Control Rig

## C++ 用法

本插件的核心是两个接口实现，主要供引擎内部 Sequencer 系统调用。如果你需要扩展或自定义混合行为，可以参考以下结构。

### 头文件引入

```cpp
#include "IMovieSceneAnimMixerBakeProvider.h"
#include "IMovieSceneEditingContextLayerResolver.h"
```

### 接口实现参考

以下是插件中两个核心类的实现模式，展示了如何将自定义动画系统接入 Anim Mixer：

**混合层解析器** — 将编辑上下文映射到 Mixer 层：

```cpp
// 来源: Private/MovieSceneMixedControlRigEditorModule.h
class FMixedControlRigLayerResolver : public IMovieSceneEditingContextLayerResolver
{
public:
    // 将 Sequencer 的 EditingContext 解析为 Anim Mixer 可识别的层对象
    virtual UObject* ResolveEditingContextToMixerLayer(
        const UMovieSceneEntitySystemLinker* Linker,
        const UObject* EditingContext) const override;
};
```

**烘焙提供器** — 提供烘焙菜单和烘焙后处理：

```cpp
// 来源: Private/MixedControlRigBakeProvider.h
class FMixedControlRigBakeProvider : public IMovieSceneAnimMixerBakeProvider
{
public:
    // 构建右键菜单中的 "Bake to Control Rig" 菜单项
    // 内部委托给 UE::ControlRig::BuildBakeToControlRigMenu()
    // 烘焙成功后自动激活 FControlRigEditMode
    virtual void BuildBakeToControlRigMenuSection(
        FMenuBuilder& MenuBuilder,
        const FAnimMixerBakeMenuParams& Params) override;
};
```

### 模块注册

插件在模块启动时注册这两个组件：

```cpp
// 来源: Private/MovieSceneMixedControlRigEditorModule.h
void FMovieSceneMixedControlRigEditorModule::StartupModule()
{
    // 注册层解析器，使 Sequencer 能将 Control Rig 上下文映射到 Mixer
    // 注册烘焙提供器，使右键菜单出现 "Bake to Control Rig" 选项
}

void FMovieSceneMixedControlRigEditorModule::ShutdownModule()
{
    // 清理注册
}
```

## Demo 示例

本插件是纯系统级集成，不提供可直接实例化的类。以下展示如何在自己的模块中实现类似的 Anim Mixer 集成：

```cpp
// MyAnimMixerIntegration.h
#pragma once

#include "IMovieSceneAnimMixerBakeProvider.h"
#include "IMovieSceneEditingContextLayerResolver.h"

class FMyLayerResolver : public IMovieSceneEditingContextLayerResolver
{
public:
    virtual UObject* ResolveEditingContextToMixerLayer(
        const UMovieSceneEntitySystemLinker* Linker,
        const UObject* EditingContext) const override
    {
        // 将你的自定义动画上下文映射到 Mixer 层
        // 返回一个 UObject* 代表混合层
        return nullptr; // 替换为实际实现
    }
};

class FMyBakeProvider : public IMovieSceneAnimMixerBakeProvider
{
public:
    virtual void BuildBakeToControlRigMenuSection(
        FMenuBuilder& MenuBuilder,
        const FAnimMixerBakeMenuParams& Params) override
    {
        // 添加自定义烘焙菜单项
        MenuBuilder.AddMenuEntry(
            NSLOCTEXT("MyPlugin", "BakeToMyRig", "Bake to My Custom Rig"),
            FText::GetEmpty(),
            FSlateIcon(),
            FUIAction(FExecuteAction::CreateLambda([Params]()
            {
                // 执行自定义烘焙逻辑
            }))
        );
    }
};
```

## 模块依赖

从头文件 `#include` 推断的依赖关系：

| 模块 | 用途 |
|---|---|
| `MovieScene` | 提供 `IMovieSceneEditingContextLayerResolver` 和 `UMovieSceneEntitySystemLinker` |
| `ControlRig` | 提供 `UE::ControlRig::BuildBakeToControlRigMenu()` 和 `FControlRigEditMode` |
| `SequencerCore` / `MovieSceneTools` | 提供 `IMovieSceneAnimMixerBakeProvider` 接口和 Anim Mixer 框架 |

## 维护状态

### 近期更新

- 2026-04-21 `eb0331ca` Anim Mixer: Bake To Control Rig and Anim Sequence support for anim mixer for binding, mixer track an
- 2026-04-17 `62f614c6` Sequencer: Fix Control Rig gizmo drawing offset in Animation Mixer with multi-layer root motion
- 2026-04-07 `8bf4fb4b` Sequencer: Restructure mixer evaluation around layers; new mask blend system
- 2026-03-31 `b48e7f74` Fix shutdown issue with MovieScene
- 2026-03-31 `c7aaaa03` Sequencer: Enable root motion extraction for control rig in Animation Mixer.

### 维护评价

- **实验性插件**：`.uplugin` 中 `IsExperimentalVersion=true`，`EnabledByDefault=false`，表明此功能尚未稳定
- **代码规模小**：仅 8 个源文件，属于轻量级集成模块
- **依赖关系清晰**：仅依赖标准的 Sequencer/ControlRig 模块，无额外第三方依赖
- **⚠️ 注意**：作为实验性插件，API 可能在未来版本中发生变化，不建议在生产环境中重度依赖
- **推荐**：如果你需要在 Sequencer 中混合 Control Rig 动画，这是目前唯一的官方方案，可以在实验项目中尝试使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieSceneMixedControlRig)
- [ControlRig 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ControlRig)（核心依赖）
- [Sequencer 编辑器](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/MovieScene)（Anim Mixer 所在模块）