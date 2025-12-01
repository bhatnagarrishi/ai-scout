import { Controller, Get, Put, Body, HttpException, HttpStatus } from '@nestjs/common';
import { NodesService } from './nodes.service'; // Service import


@Controller()
export class NodesController {
    constructor(private readonly nodesService: NodesService) { }

    @Put('nodes')
    async createNode(@Body() nodeData: any) {
        try {
            // Basic validation (can be enhanced with DTOs)
            if (!nodeData.kind || !nodeData.metadata || !nodeData.metadata.id) {
                throw new HttpException('Invalid node data: kind and metadata.id are required', HttpStatus.BAD_REQUEST);
            }
            return await this.nodesService.createOrUpdateNode(nodeData);
        } catch (error) {
            throw new HttpException(error.message, HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    @Get('graph')
    async getGraph() {
        return await this.nodesService.getGraph();
    }
}
