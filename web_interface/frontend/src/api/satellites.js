import client from './client'

/**
 * 卫星管理API
 *
 * 提供卫星的CRUD操作，替代原有的localStorage方案
 */
export const satelliteApi = {
  /**
   * 获取卫星列表
   * @param {Object} params - 查询参数
   * @param {number} params.skip - 跳过记录数
   * @param {number} params.limit - 返回记录数上限
   * @param {string} params.search - 搜索关键词
   * @param {string} params.constellation - 星座名称筛选
   * @returns {Promise<{total: number, items: Array}>}
   */
  getAll(params = {}) {
    const { skip = 0, limit = 20, search, constellation } = params
    const queryParams = new URLSearchParams()

    if (skip !== undefined) queryParams.append('skip', skip)
    if (limit !== undefined) queryParams.append('limit', limit)
    if (search) queryParams.append('search', search)
    if (constellation) queryParams.append('constellation', constellation)

    const queryString = queryParams.toString()
    const url = queryString ? `/satellites?${queryString}` : '/satellites'

    return client.get(url)
  },

  /**
   * 获取单个卫星详情
   * @param {string} id - 卫星ID
   * @returns {Promise<Object>}
   */
  getById(id) {
    return client.get(`/satellites/${id}`)
  },

  /**
   * 创建新卫星
   * @param {Object} data - 卫星数据
   * @returns {Promise<Object>}
   */
  create(data) {
    return client.post('/satellites', data)
  },

  /**
   * 更新卫星
   * @param {string} id - 卫星ID
   * @param {Object} data - 更新数据
   * @returns {Promise<Object>}
   */
  update(id, data) {
    return client.put(`/satellites/${id}`, data)
  },

  /**
   * 删除卫星
   * @param {string} id - 卫星ID
   * @returns {Promise<Object>}
   */
  delete(id) {
    return client.delete(`/satellites/${id}`)
  },

  /**
   * 批量删除卫星
   * @param {Array<string>} ids - 卫星ID数组
   * @returns {Promise<Array>}
   */
  async batchDelete(ids) {
    const results = []
    for (const id of ids) {
      try {
        const result = await this.delete(id)
        results.push({ id, success: true, result })
      } catch (error) {
        results.push({ id, success: false, error })
      }
    }
    return results
  },

  /**
   * 搜索卫星
   * @param {string} keyword - 搜索关键词
   * @param {Object} options - 其他选项
   * @returns {Promise<{total: number, items: Array}>}
   */
  search(keyword, options = {}) {
    return this.getAll({ ...options, search: keyword })
  }
}

export default satelliteApi
