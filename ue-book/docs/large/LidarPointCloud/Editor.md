# LidarPointCloudEditor 模块文档

`LidarPointCloudEditor` 是点云插件的编辑器模块，提供资产导入、编辑模式、交互工具、预览视口和属性面板等编辑器功能。

## 模块概述

该模块依赖 `LidarPointCloudRuntime`，为编辑器用户提供完整的点云资产工作流：导入 → 预览 → 编辑（选择、清理、修改） → 导出/网格化。

## 文件导入工厂

### ULidarPointCloudFactory

**头文件**：`LidarPointCloudFactory.h`

继承自 `UFactory`，负责处理拖拽导入或 Content Browser 导入。支持所有已注册的文件格式（LAS, LAZ, E57, TXT, XYZ, PTS）。

工作流程：
1. 检测文件扩展名，查找对应的 `FLidarPointCloudFileIOHandler`
2. 如果格式有 Import UI（如 ASCII 格式），弹出设置对话框
3. 调用 `ULidarPointCloudFileIO::Import` 执行实际导入
4. 创建 `ULidarPointCloud` 资产并填充数据

### FLidarPointCloudImportSettings_ASCII 导入 UI

ASCII 格式（TXT/XYZ/PTS）导入时会显示专用 UI：

- **跳过行数**（LinesToSkip）— 跳过文件头
- **分隔符检测** — 自动检测 Tab/空格/逗号等
- **列映射** — 为每列指定数据类型（Location X/Y/Z、R/G/B、Intensity、Normal X/Y/Z）
- **RGB 范围** — 设置颜色值范围（如 0-255 或 0-1）

### AssetDefinition_LidarPointCloud

**头文件**：`AssetDefinition_LidarPointCloud.h`

UE5 新的资产定义系统集成，提供：
- Content Browser 中的图标和缩略图
- 右键菜单操作
- 资产打开行为（双击打开编辑器视口）

## 编辑器模式（EdMode）

### ULidarEditorMode

**头文件**：`LidarPointCloudEdMode.h`

专用的点云编辑模式（`FEditorModeID: EM_Lidar`），继承自 `UBaseLegacyWidgetEdMode`。

激活后提供：
- 专用工具栏（Toolkit）
- 禁用普通 Actor 选择（仅允许点云选择）
- 自定义 Pivot 点（围绕选中点云旋转）
- 快捷键绑定

### 快捷键命令

**头文件**：`LidarPointCloudEditorCommands.h`

| 命令 | 说明 |
|---|---|
| `SetShowGrid` | 显示/隐藏网格 |
| `SetShowBounds` | 显示/隐藏包围盒 |
| `SetShowCollision` | 显示/隐藏碰撞 |
| `SetShowNodes` | 显示/隐藏八叉树节点 |
| `ResetCamera` | 重置相机 |
| `Center` | 居中点云 |
| `ToolkitSelect` | 选择工具 |
| `ToolkitBoxSelection` | 框选工具 |
| `ToolkitPolygonalSelection` | 多边形选择工具 |
| `ToolkitLassoSelection` | 套索选择工具 |
| `ToolkitPaintSelection` | 画笔选择工具 |

## 交互工具（Interactive Tools）

编辑器工具基于 UE5 的 Interactive Tools Framework 实现，提供了丰富的点云编辑能力。

### 工具基类

| 类 | 说明 |
|---|---|
| `ULidarEditorToolBase` | 所有工具的基类 |
| `ULidarEditorToolClickDragBase` | 支持点击拖拽的工具基类 |
| `ULidarEditorToolSelectionBase` | 选择工具基类，支持框选/多边形/套索/画笔 |

### 选择工具

#### 框选（Box Selection）

`ULidarEditorToolBoxSelection` — 在视口中拖拽矩形区域选择点。
- 支持 Shift 加选、Ctrl 减选
- 选择结果实时显示

#### 多边形选择（Polygonal Selection）

`ULidarEditorToolPolygonalSelection` — 点击创建多边形顶点，闭合后选择内部点。
- 支持吸附（Snap）

#### 套索选择（Lasso Selection）

`ULidarEditorToolLassoSelection` — 自由绘制选择区域。

#### 画笔选择（Paint Selection）

`ULidarEditorToolPaintSelection` — 使用圆形画笔涂抹选择点。

| 参数 | 说明 |
|---|---|
| `BrushRadius` | 画笔半径（0-8196） |

### 选择工具操作面板

选择工具激活后，面板提供以下操作：

**Selection 类别**：
| 操作 | 说明 |
|---|---|
| `Clear` | 清除选择 |
| `Invert` | 反选 |

**Cleanup 类别**：
| 操作 | 说明 |
|---|---|
| `DeleteSelected` | 删除选中点 |
| `DeleteHidden` | 删除隐藏点 |
| `HideSelected` | 隐藏选中点 |
| `ResetVisibility` | 重置所有点可见性 |

**Normals 类别**：
| 操作 | 说明 |
|---|---|
| `CalculateNormals` | 计算法线 |
| Quality | 法线质量（1-100） |
| NoiseTolerance | 噪声容差 |

**Merge & Extract 类别**：
| 操作 | 说明 |
|---|---|
| `Extract` | 提取选中点（替换原数据） |
| `ExtractAsCopy` | 提取选中点为副本 |

**Meshing 类别**：
| 操作 | 说明 |
|---|---|
| `BuildStaticMesh` | 从选中点创建 Static Mesh |
| MaxMeshingError | 最大网格化误差 |
| bMergeMeshes | 是否合并网格 |
| bRetainTransform | 是否保留原始变换 |

### 对齐工具（Align）

`ULidarEditorToolAlign` — 对齐多个点云资产。

| 操作 | 说明 |
|---|---|
| `AlignAroundWorldOrigin` | 围绕世界原点对齐 |
| `AlignAroundOriginalCoordinates` | 围绕原始坐标对齐 |
| `ResetAlignment` | 重置对齐 |

### 合并工具（Merge）

`ULidarEditorToolMerge` — 合并多个点云。

| 参数/操作 | 说明 |
|---|---|
| bReplaceSourceActorsAfterMerging | 合并后是否替换源 Actor |
| `MergeActors` | 合并 Actor（创建新资产） |
| `MergeData` | 合并数据（追加到当前资产） |

### 碰撞工具（Collision）

`ULidarEditorToolCollision` — 管理碰撞。

| 参数/操作 | 说明 |
|---|---|
| OverrideMaxCollisionError | 覆盖最大碰撞误差（0-2000） |
| `BuildCollision` | 构建碰撞 |
| `RemoveCollision` | 移除碰撞 |

### 网格化工具（Meshing）

`ULidarEditorToolMeshing` — 从点云生成 Static Mesh。

| 参数/操作 | 说明 |
|---|---|
| MaxMeshingError | 最大网格化误差（0 表示最高质量） |
| bMergeMeshes | 是否合并为单个网格 |
| bRetainTransform | 是否保留原始变换 |
| `BuildStaticMesh` | 执行网格化 |

### 法线工具（Normals）

`ULidarEditorToolNormals` — 计算法线。

| 参数/操作 | 说明 |
|---|---|
| Quality | 质量（1-100），越高越精确但越慢 |
| NoiseTolerance | 噪声容差，越高越抗噪但丢失细节 |
| `CalculateNormals` | 执行计算 |

## 预览视口

### FLidarPointCloudEditorViewportClient

**头文件**：`LidarPointCloudEditorViewportClient.h`

专用的编辑器预览视口客户端，双击点云资产时打开。

功能：
- 3D 点云预览
- 相机控制（旋转、平移、缩放）
- 渲染参数实时调整
- 显示模式切换（网格/包围盒/碰撞/节点）

### FLidarPointCloudEditorViewport

**头文件**：`LidarPointCloudEditorViewport.h`

视口 Widget，嵌入到编辑器面板中。

## 编辑器辅助功能

### FLidarPointCloudEditorHelper

**头文件**：`LidarPointCloudEditorHelper.h`

编辑器辅助类，提供：
- 点选择逻辑
- 框选/多边形选择的几何计算
- 编辑器状态管理

### FLidarPointCloudStyle

**头文件**：`LidarPointCloudStyle.h`

管理插件的编辑器样式，包括图标和 UI 主题。

### ULidarPointCloudEditorTools

**头文件**：`LidarPointCloudEditorTools.h`

注册编辑器工具到 Interactive Tools Framework。

## Actor 工厂

### ActorFactoryLidarPointCloud

**头文件**：`ActorFactoryLidarPointCloud.h`

当从 Content Browser 拖拽点云资产到场景时，自动创建 `ALidarPointCloudActor` 并设置 `ULidarPointCloudComponent`。
