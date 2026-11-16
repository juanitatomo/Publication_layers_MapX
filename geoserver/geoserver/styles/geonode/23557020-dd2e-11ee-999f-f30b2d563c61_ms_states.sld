<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<StyledLayerDescriptor version="1.0.0" xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NamedLayer>
    <Name>Default Polygon</Name>
    <UserStyle>
      <Name>Default Polygon</Name>
      <Title>Default Polygon</Title>
      <FeatureTypeStyle>
        <Rule>
          <Name>&gt;= 1 and &lt; 6.4444</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>ogc_fid</PropertyName>
                <Literal>1</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>ogc_fid</PropertyName>
                <Literal>6.4444</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#f7fcfd</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#777777</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 6.4444 and &lt; 11.8889</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>ogc_fid</PropertyName>
                <Literal>6.4444</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>ogc_fid</PropertyName>
                <Literal>11.8889</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#e0ecf4</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#777777</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 11.8889 and &lt; 17.3333</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>ogc_fid</PropertyName>
                <Literal>11.8889</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>ogc_fid</PropertyName>
                <Literal>17.3333</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#bfd3e6</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#777777</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 17.3333 and &lt; 22.7778</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>ogc_fid</PropertyName>
                <Literal>17.3333</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>ogc_fid</PropertyName>
                <Literal>22.7778</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#9ebcda</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#777777</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 22.7778 and &lt; 28.2222</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>ogc_fid</PropertyName>
                <Literal>22.7778</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>ogc_fid</PropertyName>
                <Literal>28.2222</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#8c96c6</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#777777</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 28.2222 and &lt; 33.6667</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>ogc_fid</PropertyName>
                <Literal>28.2222</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>ogc_fid</PropertyName>
                <Literal>33.6667</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#8c6bb1</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#777777</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 33.6667 and &lt; 39.1111</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>ogc_fid</PropertyName>
                <Literal>33.6667</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>ogc_fid</PropertyName>
                <Literal>39.1111</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#88419d</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#777777</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 39.1111 and &lt; 44.5556</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>ogc_fid</PropertyName>
                <Literal>39.1111</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThan>
                <PropertyName>ogc_fid</PropertyName>
                <Literal>44.5556</Literal>
              </PropertyIsLessThan>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#810f7c</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#777777</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>&gt;= 44.5556 and &lt;= 50</Name>
          <Filter xmlns="http://www.opengis.net/ogc">
            <And>
              <PropertyIsGreaterThanOrEqualTo>
                <PropertyName>ogc_fid</PropertyName>
                <Literal>44.5556</Literal>
              </PropertyIsGreaterThanOrEqualTo>
              <PropertyIsLessThanOrEqualTo>
                <PropertyName>ogc_fid</PropertyName>
                <Literal>50</Literal>
              </PropertyIsLessThanOrEqualTo>
            </And>
          </Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#4d004b</CssParameter>
              <CssParameter name="fill-opacity">1</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#777777</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>