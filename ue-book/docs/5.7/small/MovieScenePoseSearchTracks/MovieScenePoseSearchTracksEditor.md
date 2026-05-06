# Movie Scene Pose Search Tracks

> Sequencer pose search tracks using the Anim Mixer

| 属性 | 值 |
|---|---|
| 中文名 | 姿态搜索缝合轨道 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器配置与轨道预设） |
| 模块 | `MovieScenePoseSearchTracks` (Runtime), `MovieScenePoseSearchTracksEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-26 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieScenePoseSearchTracks) | |

---

## 用途

该插件基于 `UAFPoseSearch`（姿态搜索数据库）和 `MovieSceneAnimMixer`（动画混合器）为 Sequencer 提供 **缝合动画轨道**（Stitch Anim Track）。用户可以在 Sequencer 中为一个骨骼对象添加缝合轨道，通过拾取姿态搜索数据库中的动画片段，自动在时间线上生成过渡槽位，用于实现角色动画的流畅混合与衔接。主要解决传统 PoseWheel 等手动混合方式在 Sequencer 中流程复杂、难以复用的问题，让动画师能够直接以姿态搜索算法驱动动画混合。

---

## 使用场景

- 在 Sequencer 中制作角色动画过场时，需要自然衔接多个动作片段（如走路→跑步→跳跃）
- 希望利用姿态搜索数据库（PoseSearchDatabase）自动匹配最佳过渡动画，减少手动调整关键帧
- 使用 Anim Mixer 混合架构，需要 Sequencer 提供高级轨道支持

---

## 蓝图用法

该插件**没有暴露任何 BlueprintCallable 或 BlueprintReadWrite 的 UFunction/UProperty**。所有功能均为编辑器专用，通过 C++ 的轨道编辑器实现。在蓝图中无法直接使用该插件中的类。

---

## C++ 用法

### 头文件引入

```cpp
// 运行时模块
#include "MovieScenePoseSearchTracks.h"          // 如果需要使用运行时数据模型
#include "MovieSceneStitchAnimTrack.h"           // 缝合动画轨道
#include "MovieSceneStitchAnimSection.h"         // 缝合动画片段

// 编辑器模块（仅在编辑器模块中可用）
#include "TrackEditors/StitchAnimTrackEditor.h"  // 轨道编辑器
```

### 基本用法

在自定义 Sequencer 扩展中注册轨道编辑器：

```cpp
// 在模块 StartupModule 中注册（参见 MovieScenePoseSearchTracksEditorModule.cpp）
FStitchAnimTrackEditor::CreateTrackEditor(OwningSequencer);
```

典型注册流程：

```cpp
void FMovieScenePoseSearchTracksEditorModule::StartupModule()
{
    // 注册轨道编辑器
    FStitchAnimTrackEditor::CreateTrackEditor(Sequencer);
}
```

### 进阶用法

1. **通过 Asset 拖拽创建轨道**  
   当用户将一个 `UPoseSearchDatabase` 资产拖入 Sequencer 时，`HandleAssetAdded` 被触发，自动创建缝合轨道并绑定到指定对象。

2. **自定义右键菜单构建**  
   `BuildObjectBindingTrackMenu` 在对象绑定右键菜单中添加“添加缝合动画轨道”入口，通过 `BuildAddAnimationSubMenu` 生成子菜单，列出骨骼对应的姿态搜索数据库资产。

3. **轨道外观自定义**  
   `FStitchAnimSection` 类重写 `PaintSection` 等方法，实现缝合片段的可视化渲染（显示名称、持续时间、是否可编辑等）。

4. **数据模型**  
   运行时模块（`MovieScenePoseSearchTracks`）提供：
   - `UMovieSceneStitchAnimTrack`：轨道容器，管理多个缝合片段
   - `UMovieSceneStitchAnimSection`：单个片段，持有 `UPoseSearchDatabase` 引用以及时间范围

   这些类通常不直接在 C++ 中手动创建，而是通过编辑器交互自动生成。

---

## Demo 示例

由于该插件高度依赖编辑器交互，无法提供独立可编译的最小示例。以下是在自定义模块中集成轨道编辑器的最简代码：

**MySequencerExtension.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

class FMySequencerExtensionModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MySequencerExtension.cpp**
```cpp
#include "MySequencerExtension.h"
#include "ISequencerModule.h"
#include "TrackEditors/StitchAnimTrackEditor.h"

void FMySequencerExtensionModule::StartupModule()
{
    ISequencerModule& SequencerModule = FModuleManager::LoadModuleChecked<ISequencerModule>("Sequencer");
    // 注册缝合轨道编辑器
    SequencerModule.RegisterTrackEditor(FOnCreateTrackEditor::CreateStatic(&FStitchAnimTrackEditor::CreateTrackEditor));
}

void FMySequencerExtensionModule::ShutdownModule()
{
    // 反注册（需保存 Handle）
}

IMPLEMENT_MODULE(FMySequencerExtensionModule, MySequencerExtension);
```

---

## 模块依赖

### 运行时模块 `MovieScenePoseSearchTracks`

| 模块 | 用途 |
|---|---|
| `MovieSceneAnimMixer` | 动画混合器运行时支持，提供混合核心 |
| `UAFPoseSearch` | 姿态搜索数据库，提供动画片段检索算法 |

### 编辑器模块 `MovieScenePoseSearchTracksEditor`

| 模块 | 用途 |
|---|---|
| `MovieScenePoseSearchTracks` | 引用运行时数据模型（UMovieSceneStitchAnimTrack等） |
| `Sequencer` | 轨道编辑器扩展（ISequencerTrackEditor） |
| `MovieSceneTools` | 通用 Sequencer 工具（如章节绘制、资源拖放） |
| `UnrealEd` | 编辑器基础设施（资产动作、菜单构建） |

> **注意**：省略了 Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore 等标准依赖。

---

## 维护状态

### 近期更新

| 日期 | 提交 | 解读 |
|---|---|---|
| 2025-09-03 | `072d3134` | Sequencer: Minor Stitch Track UX fixes.（修复用户体验问题） |
| 2025-07-31 | `bdedc2af` | PoseSearch - support for PSD search returning multiple results（姿态搜索支持返回多个结果） |
| 2025-07-24 | `4d8395fa` | PoseSearch - deprecating pose search database TArray<FInstancedStruct> AnimationAssets in favor of T（数据库资产结构重构） |
| 2025-06-27 | `ee0441e9` | UAF: Rename/move plugins（插件重命名/移动） |
| 2025-06-26 | `effdabd2` | UAF: Moved/renamed AnimNext and AnimNextAnimGraph plugins（插件初始创建/移动） |

### 维护评价

- **创建时间**：2025-06-26，非常新
- **近期更新**：2025-09-03 有 UX 修复，2025-07-31 有功能增强，更新频率较高
- **活跃状态**：处于活跃开发中，但标记为实验性插件
- **已知限制**：依赖 `MovieSceneAnimMixer` 和 `UAFPoseSearch`，这两个插件同样处于实验阶段，API 可能变动
- **推荐度**：适合关注姿态搜索和动画混合前沿开发的团队使用，生产环境需谨慎评估稳定性

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieScenePoseSearchTracks)
- [官方文档](https://docs.unrealengine.com/5.7/AnimMixer)（请参考 Anim Mixer 通用文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieScenePoseSearchTracks/Tests)（暂无独立测试，相关测试整合在 MovieSceneAnimMixer 测试套件中）