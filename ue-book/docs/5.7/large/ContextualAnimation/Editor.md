# ContextualAnimation — Editor 模块

Editor 模块提供上下文动画场景资产的完整编辑器集成，包括专用编辑器工具、Sequencer 集成、预览场景和自定义 Property 面板。

## 模块信息

- **模块名**: `ContextualAnimationEditor`
- **类型**: Editor
- **Build.cs**: `Source/ContextualAnimationEditor/ContextualAnimationEditor.Build.cs`

## 源码文件结构

### Editor 工具

| 文件 | 类型 | 说明 |
|---|---|---|
| `ContextualAnimAssetEditorToolkit.h/cpp` | `FContextualAnimAssetEditorToolkit` | 场景资产编辑器主窗口（Asset Editor） |
| `ContextualAnimViewModel.h/cpp` | `FContextualAnimViewModel` | 编辑器的 ViewModel 层，管理编辑状态 |
| `ContextualAnimEdMode.h/cpp` | `FContextualAnimEdMode` | 自定义编辑模式（EdMode），用于 3D 视口中的交互 |
| `ContextualAnimTypeActions.h/cpp` | `FContextualAnimTypeActions` | 资产类型注册（右键菜单、双击打开等） |
| `ContextualAnimFactory.h/cpp` | `UContextualAnimFactory` | 资产工厂（Content Browser 中创建新资产） |
| `ContextualAnimEditorStyle.h/cpp` | `FContextualAnimEditorStyle` | 编辑器 UI 样式定义 |
| `ContextualAnimEditorTypes.h/cpp` | — | 编辑器专用类型定义 |
| `ContextualAnimAssetEditorCommands.h/cpp` | `FContextualAnimAssetEditorCommands` | 编辑器快捷键/命令定义 |

### 视口和预览

| 文件 | 类型 | 说明 |
|---|---|---|
| `SContextualAnimViewport.h/cpp` | `SContextualAnimViewport` | 自定义 3D 视口 Widget |
| `SContextualAnimViewportToolbar.h/cpp` | `SContextualAnimViewportToolbar` | 视口工具栏 |
| `ContextualAnimViewportClient.h/cpp` | `FContextualAnimViewportClient` | 视口客户端（处理输入、渲染） |
| `ContextualAnimPreviewScene.h/cpp` | `FContextualAnimPreviewScene` | 预览场景管理（Actor 创建、动画播放控制） |
| `SContextualAnimAssetBrowser.h/cpp` | `SContextualAnimAssetBrowser` | 动画资产浏览器面板 |
| `SContextualAnimNewAnimSetDialog.h/cpp` | `SContextualAnimNewAnimSetDialog` | 创建新 AnimSet 的对话框 |

### Sequencer 集成

| 文件 | 类型 | 说明 |
|---|---|---|
| `ContextualAnimMovieSceneSequence.h/cpp` | `UContextualAnimMovieSceneSequence` | 自定义 MovieScene Sequence |
| `ContextualAnimMovieSceneTrack.h/cpp` | `UContextualAnimMovieSceneTrack` | 交互动画的 Sequencer Track |
| `ContextualAnimMovieSceneTrackEditor.h/cpp` | `FContextualAnimMovieSceneTrackEditor` | Track Editor（注册自定义 Track） |
| `ContextualAnimMovieSceneSection.h/cpp` | `UContextualAnimMovieSceneSection` | Sequencer Section |
| `ContextualAnimMovieSceneNotifyTrack.h/cpp` | `UContextualAnimMovieSceneNotifyTrack` | 通知专用 Track |
| `ContextualAnimMovieSceneNotifyTrackEditor.h/cpp` | `FContextualAnimMovieSceneNotifyTrackEditor` | 通知 Track Editor |
| `ContextualAnimMovieSceneNotifySection.h/cpp` | `UContextualAnimMovieSceneNotifySection` | 通知 Section |

### Detail Customization

| 文件 | 类型 | 说明 |
|---|---|---|
| `DetailCustomizations/ContextualAnimSceneAssetDetailCustom.h/cpp` | `FContextualAnimSceneAssetDetailCustom` | SceneAsset 属性面板自定义 |
| `DetailCustomizations/ContextualAnimNotifySectionDetailCustom.h/cpp` | `FContextualAnimNotifySectionDetailCustom` | 通知 Section 属性面板自定义 |

## 编辑器功能

### 场景资产编辑器

`FContextualAnimAssetEditorToolkit` 提供了专用的场景资产编辑界面，包含：

- **3D 预览视口**：实时预览所有角色的动画和空间对齐
- **AnimSet 管理**：添加/删除/编辑动画集合
- **动画轨道编辑**：为每个角色指定动画、设置参数
- **Warp Point 可视化**：在视口中显示和编辑对齐点
- **Selection Criteria 配置**：为每个动画轨道配置选择标准

### Sequencer 集成

通过 `FContextualAnimMovieSceneTrackEditor`，交互场景可以被放入 Sequencer 时间轴中：

- 每个角色在时间轴上有独立的动画 Section
- 支持通知（Notify）Track 用于标记关键事件
- 可以在 Sequencer 中预览完整的交互流程

### EdMode

`FContextualAnimEdMode` 提供了自定义编辑模式，在场景编辑器的 3D 视口中：

- 可视化角色的对齐位置
- 拖拽调整 Warp Point
- 实时预览选择标准的影响区域（如 Cone 和 TriggerArea 的可视化）

## 依赖关系

Editor 模块对 Runtime 模块的依赖：

```
ContextualAnimationEditor
├── ContextualAnimation (Runtime 模块)
├── MotionWarping
├── GameplayTags
├── AIModule / NavigationSystem (编辑器辅助)
├── UnrealEd / EditorFramework (编辑器框架)
├── Sequencer / MovieScene / MovieSceneTracks (Sequencer 集成)
├── Persona / AnimGraph (动画编辑器集成)
└── PropertyEditor / DetailCustomizations (属性面板)
```
