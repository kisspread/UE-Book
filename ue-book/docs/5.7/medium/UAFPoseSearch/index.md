# UAF Pose Search

> Pose Search integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF姿态搜索 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFPoseSearch` (Runtime), `UAFPoseSearchUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-20 |
| 年龄标签 | 🆕（约1年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFPoseSearch) | |

## 总体用途

为 **UAF（Unreal Animation Framework）** 提供姿态搜索集成。通过运动匹配（Motion Matching）所需的姿态特征提取、轨迹生成、姿态数据库构建等功能，实现基于动画姿态相似度的运行时动画选择。包含运行时核心模块与编辑器预处理模块，用于生成和查询姿态特征数据。

## 模块列表

| 模块 | 类型 | 一句话说明 | 文档 |
|---|---|---|---|
| `UAFPoseSearch` | Runtime | 运行时姿态搜索核心，提供搜索请求、特征计算、数据库查询等 API | [UAFPoseSearch.md](UAFPoseSearch.md) |
| `UAFPoseSearchUncookedOnly` | Runtime | 编辑器未烘焙阶段使用的姿态数据库构建与特征提取工具 | [UAFPoseSearchUncookedOnly.md](UAFPoseSearchUncookedOnly.md) |

## 使用场景

- **运动匹配角色动画**：为角色创建自然的行走、跑步、转向等过渡动画，基于当前运动轨迹匹配最合适的动画姿势。
- **自定义动画系统**：结合 UAF 框架，扩展自有的动画选择逻辑，利用姿态搜索提高动画流畅性。
- **编辑器预处理**：在打包前对 Animation Sequence 进行特征提取和数据库构建，提高运行时查询效率。

## 维护状态

### 近期更新

- 2025-10-03 `ff6147ec` - Updated UAF Trajectory functions to have an execution pin.
- 2025-10-03 `61a8ba04` - Added UAF GenerateTrajectory version for CharacterMovementComponent.
- 2025-10-01 `604a7718` - PoseSearch - fix for MM trait timeline and MM node interaction blendstack synchronizations
- 2025-09-04 `d443289c` - PoseSearch
- 2025-08-20 `6cd89387` - PoseSearch - making FPoseSearchColumn::InterruptMode pinnable

### 维护评价

该插件为实验性项目，创建仅一年，近期（2025年10月）仍有功能性更新和修复，属于**活跃维护**状态。由于是 UAF 框架的特定扩展，推荐在使用 UAF 动画系统的项目中使用。注意：实验性版本 API 可能不稳定，建议在稳定版本发布后再用于生产。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFPoseSearch)
- [模块文档：UAFPoseSearch](UAFPoseSearch.md)
- [模块文档：UAFPoseSearchUncookedOnly](UAFPoseSearchUncookedOnly.md)